import dill
import json
import kafka
import fastapi

from api import db
from api import features
from api import models
from api import processors
from api import sinks
import psycopg
import sqlmodel as sqlm
import celery

router = fastapi.APIRouter()


RUNNER = celery.Celery("experiments", broker="redis://redis:6379/0")


@RUNNER.task
def run_inference(features_id, model_id, sink_id):
    with db.session() as session:
        feature_set = session.get(features.Features, features_id)
        processor = session.get(processors.Processor, feature_set.processor_id)
        model = session.get(models.Model, model_id)

    model_obj = dill.loads(model.content)

    sink = session.get(sinks.Sink, sink_id)
    producer = kafka.KafkaProducer(
        bootstrap_servers=[sink.url],
        key_serializer=str.encode,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    # Let's query the view to see what it contains. That way we can associate each feature with
    # a name.
    conn = psycopg.connect(processor.url)
    with conn.cursor() as cur:
        cur.execute(f"SHOW COLUMNS FROM {feature_set.name}")
        schema = cur.fetchall()
        columns = ["mz_timestamp", "mz_diff"] + [c[0] for c in schema]

    conn = psycopg.connect(processor.url)
    with conn.cursor() as cur:
        for row in cur.stream(f"TAIL {feature_set.name}"):
            named_features = dict(zip(columns, row))
            key = named_features.pop(feature_set.key_field)
            del named_features["mz_timestamp"]
            del named_features["mz_diff"]

            prediction = model_obj.predict_proba_one(named_features)
            producer.send(
                topic="predictions",
                key=f"{key}#{model.name}",
                value={
                    "features": named_features,
                    "prediction": prediction,
                },
            )


class Experiment(sqlm.SQLModel, table=True):
    id: int | None = sqlm.Field(default=None, primary_key=True)
    name: str

    features_id: int = sqlm.Field(foreign_key="features.id")
    target_id: int = sqlm.Field(foreign_key="target.id")
    model_id: int = sqlm.Field(foreign_key="model.id")
    runner_id: int = sqlm.Field(foreign_key="runner.id")
    sink_id: int = sqlm.Field(foreign_key="sink.id")

    def create(self, session):
        session.add(self)
        session.commit()
        session.refresh(self)

        run_inference.delay(
            features_id=self.features_id,
            model_id=self.model_id,
            sink_id=self.sink_id,
        )

        return self


@router.post("/")
def create_experiment(experiment: Experiment):
    with db.session() as session:
        return experiment.create(session)


@router.get("/")
def read_experiment(offset: int = 0, limit: int = fastapi.Query(default=100, lte=100)):
    with db.session() as session:
        experiment = session.exec(
            sqlm.select(Experiment).offset(offset).limit(limit)
        ).all()
        return experiment


@router.get("/{experiment_id}")
def read_experiment(experiment_id: int):
    with db.session() as session:
        experiment = session.get(Experiment, experiment_id)
        if not experiment:
            raise fastapi.HTTPException(status_code=404, detail="Experiment not found")
        return experiment
