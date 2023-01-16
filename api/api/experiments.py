import base64
import datetime as dt
import json

import celery
import dill
import fastapi
import kafka
import sqlmodel as sqlm
from fastapi.encoders import jsonable_encoder

from api import (  # isort:skip
    db,
    feature_sets,
    models,
    processors,
    runners,
    sinks,
    targets,
    tasks,
)

router = fastapi.APIRouter()

RUNNER = celery.Celery("experiments", broker="redis://redis:6379/0")


@RUNNER.task
def run_inference(experiment_id):
    with db.session() as session:
        experiment = session.get(Experiment, experiment_id)
        sink = experiment.sink
        feature_set = experiment.feature_set
        processor = feature_set.processor

    producer = kafka.KafkaProducer(
        bootstrap_servers=[sink.url],
        key_serializer=str.encode,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    model_last_fetched_at = dt.datetime.min

    for x in processor.stream(feature_set.name):
        key = x.pop(feature_set.key_field)

        # Refresh model every 30 seconds
        if (now := dt.datetime.now()) - model_last_fetched_at > dt.timedelta(
            seconds=experiment.sync_seconds
        ):
            with db.session() as session:
                model_state = session.get(Experiment, experiment_id).model_state
                model_obj = dill.loads(model_state)
            model_last_fetched_at = now

        prediction = model_obj.predict(x)
        producer.send(
            topic=f"predictions_{experiment_id}",
            key=str(key),
            value={
                "feature_set": x,
                "prediction": prediction,
            },
        )


@RUNNER.task
def run_training(experiment_id):
    with db.session() as session:
        experiment = session.get(Experiment, experiment_id)
        target = experiment.target
        processor = target.processor

    processor.execute(
        f"""
    CREATE VIEW learning_queue_{experiment_id} AS (
        SELECT
            t.{target.target_field} AS ground_truth,
            p.feature_set
        FROM {target.name} t
        INNER JOIN predictions_{experiment_id} p ON
            CAST(t.{target.key_field} as INTEGER) = CAST(p.key AS INTEGER)
    )
    """
    )

    model_obj = dill.loads(experiment.model_state)
    model_last_dumped_at = dt.datetime.now()
    n_samples_trained_on = 0

    for sample in processor.stream(f"learning_queue_{experiment_id}"):
        model_obj.learn(sample["feature_set"], sample["ground_truth"])
        n_samples_trained_on += 1

        # Dump models every 30 seconds
        if (now := dt.datetime.now()) - model_last_dumped_at > dt.timedelta(
            seconds=experiment.sync_seconds
        ):
            with db.session() as session:
                experiment.model_state = dill.dumps(model_obj)
                experiment.n_samples_trained_on += n_samples_trained_on
                n_samples_trained_on = 0
                session.add(experiment)
                session.commit()
                model_last_dumped_at = now


class Experiment(sqlm.SQLModel, table=True):  # type: ignore[call-arg]
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str
    model_state: bytes | None = sqlm.Field(default=None)
    n_samples_trained_on: int = sqlm.Field(default=0)
    sync_seconds: int = sqlm.Field(default=20)

    feature_set_id: int = sqlm.Field(foreign_key="feature_set.id")
    feature_set: feature_sets.FeatureSet = sqlm.Relationship(
        back_populates="experiments"
    )
    target_id: int = sqlm.Field(foreign_key="target.id")
    target: targets.Target = sqlm.Relationship(back_populates="experiments")
    model_id: int = sqlm.Field(foreign_key="model.id")
    model: models.Model = sqlm.Relationship(back_populates="experiments")
    runner_id: int = sqlm.Field(foreign_key="runner.id")
    runner: runners.Runner = sqlm.Relationship(back_populates="experiments")
    sink_id: int = sqlm.Field(foreign_key="sink.id")
    sink: sinks.Sink = sqlm.Relationship(back_populates="experiments")

    def create(self, session):

        # target.processor = feature_set.processor
        feature_set = session.get(feature_sets.FeatureSet, self.feature_set_id)
        target = session.get(targets.Target, self.target_id)
        if feature_set.processor_id != target.processor_id:
            raise ValueError("Feature set and target must be using the same processor")

        # target.task = model.task
        model = session.get(models.Model, self.model_id)
        if target.task != model.task:
            raise ValueError("Target and model must have the same task")

        model = session.get(models.Model, self.model_id)
        self.model_state = model.content

        session.add(self)
        session.commit()
        session.refresh(self)

        self.create_predictions_view()
        self.create_performance_view()
        run_inference.delay(self.id)
        if hasattr(dill.loads(model.content), "learn"):
            run_training.delay(self.id)

        return self

    def create_predictions_view(self):

        with db.session() as session:
            target = session.get(targets.Target, self.target_id)
            sink = session.get(sinks.Sink, self.sink_id)
            processor = session.get(processors.Processor, target.processor_id)

        if target.task == tasks.TaskEnum.binary_clf.value:
            prediction_type = "JSONB"
        elif target.task == tasks.TaskEnum.regression:
            prediction_type = "FLOAT"
        else:
            raise NotImplementedError

        drop_views = f"""
    DROP VIEW IF EXISTS predictions_{self.id};
    DROP VIEW IF EXISTS predictions_raw_{self.id};
    DROP SOURCE IF EXISTS predictions_src_{self.id};"""

        create_views = f"""
    CREATE MATERIALIZED SOURCE predictions_src_{self.id}
    FROM KAFKA BROKER '{sink.url}' TOPIC 'predictions_{self.id}'
    KEY FORMAT BYTES
    VALUE FORMAT BYTES
    INCLUDE KEY AS key;

    CREATE VIEW predictions_raw_{self.id} AS (
        SELECT
            CONVERT_FROM(key, 'utf8') AS key,
            CAST(CONVERT_FROM(data, 'utf8') AS JSONB) AS prediction
        FROM predictions_src_{self.id}
    );

    CREATE VIEW predictions_{self.id} AS (
        SELECT
            key,
            CAST(prediction ->> 'feature_set' AS JSONB) AS feature_set,
            CAST(prediction ->> 'prediction' AS {prediction_type}) AS prediction
        FROM predictions_raw_{self.id}
    )"""

        if (
            target.task == tasks.TaskEnum.binary_clf.value
            or target.task == tasks.TaskEnum.regression
        ):

            processor.execute(
                f"""
    {drop_views}
    {create_views}
    """
            )

        else:
            raise NotImplementedError

    def create_performance_view(self):

        with db.session() as session:
            target = session.get(targets.Target, self.target_id)
            processor = session.get(processors.Processor, target.processor_id)

        if target.task == tasks.TaskEnum.binary_clf.value:

            processor.execute(
                f"""
    CREATE VIEW performance_{self.id} AS (
        SELECT
            COALESCE((tn + tp) / NULLIF(total::FLOAT, 0), 0) AS accuracy,
            COALESCE(tp / NULLIF((tp + fn)::FLOAT, 0), 0) AS recall,
            COALESCE(tp / NULLIF((tp + fp)::FLOAT, 0), 0) AS precision
        FROM (
            -- Confusion matrix
            SELECT
                COUNT(*) FILTER (WHERE y_pred AND y_true) AS tp,
                COUNT(*) FILTER (WHERE y_pred AND NOT y_true) AS fp,
                COUNT(*) FILTER (WHERE NOT y_pred AND NOT y_true) AS tn,
                COUNT(*) FILTER (WHERE NOT y_pred AND y_true) AS fn,
                COUNT(*) AS total
            FROM (
                -- Labels <> predictions
                SELECT
                    y.{target.target_field} AS y_true,
                    CAST(p.prediction ->> 'true' AS FLOAT) > 0.5 AS y_pred
                FROM predictions_{self.id} p
                INNER JOIN {target.name} y ON
                    CAST(y.{target.key_field} AS INTEGER) = CAST(p.key AS INTEGER)
            )
        )
    )"""
            )

        elif target.task == tasks.TaskEnum.regression:
            processor.execute(
                f"""
    CREATE VIEW performance_{self.id} AS (
        SELECT
            AVG(POW(y_true - y_pred, 2)) AS mse,
            AVG(ABS(y_true - y_pred)) AS mae
        FROM (
            -- Labels <> predictions
            SELECT
                y.{target.target_field} AS y_true,
                CAST(p.prediction AS FLOAT) AS y_pred
            FROM predictions_{self.id} p
            INNER JOIN {target.name} y ON
                CAST(y.{target.key_field} AS INTEGER) = CAST(p.key AS INTEGER)
        )
    )"""
            )

        else:
            raise NotImplementedError


@router.post("/")
def create_experiment(experiment: Experiment):
    with db.session() as session:
        exp = experiment.create(session)
        # model_content needs to be encoded if we want to return it here
        exp.model_state = jsonable_encoder(
            exp.model_state,
            custom_encoder={bytes: lambda v: base64.b64encode(v).decode("utf-8")},
        )
        return exp


@router.get("/")
def read_experiments(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        return session.exec(
            sqlm.select(
                Experiment.name,
                Experiment.id,
                Experiment.feature_set_id,
                Experiment.target_id,
                Experiment.model_id,
                Experiment.runner_id,
                Experiment.sink_id,
            )
            .offset(offset)
            .limit(limit)
        ).all()


@router.get("/{experiment_id}", response_model=Experiment)
def read_experiment(experiment_id: int):
    with db.session() as session:
        experiment = session.exec(
            sqlm.select(
                Experiment.name,
                Experiment.id,
                Experiment.feature_set_id,
                Experiment.target_id,
                Experiment.model_id,
                Experiment.runner_id,
                Experiment.sink_id,
            ).where(Experiment.id == experiment_id)
        ).first()
        if not experiment:
            raise fastapi.HTTPException(status_code=404, detail="Experiment not found")
        return experiment


@router.get("/{experiment_id}/monitor")
def monitor_experiment(experiment_id: int):
    with db.session() as session:
        experiment = session.exec(
            sqlm.select(Experiment).where(Experiment.id == experiment_id)
        ).first()
        processor = experiment.target.processor
        n_samples = processor.get_first_row(
            f"SELECT COUNT(*) AS n FROM learning_queue_{experiment_id}"
        )["n"]
        return {
            "now": dt.datetime.now().isoformat(),
            "training_progress": experiment.n_samples_trained_on / n_samples
            if n_samples
            else 0,
            **processor.get_first_row(f"SELECT * FROM performance_{experiment_id}"),
        }
