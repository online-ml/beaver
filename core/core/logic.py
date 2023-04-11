import datetime as dt
import json
import fastapi
import sqlmodel as sqlm
from core import db, enums, models, infra


def iter_dataset(experiment_name: str, since: dt.datetime):

    dataset_name = f"{experiment_name}_dataset"

    with db.session() as session:
        experiment = session.get(models.Experiment, experiment_name)
        project = experiment.project
        project.stream_processor
        experiment.feature_set
        project.target

    if project.stream_processor.protocol == enums.StreamProcessor.sqlite.value:

        # Unlabelled samples that need predicting
        query = f"""
        SELECT
            features.{experiment.feature_set.ts_field} AS ts,
            features.{experiment.feature_set.key_field} AS key,
            features.{experiment.feature_set.features_field} AS features,
            NULL as target
        FROM {experiment.feature_set.name} features
        WHERE key NOT IN (
            SELECT key
            FROM messages
            WHERE topic = '{project.predictions_topic_name}'
            AND JSON_EXTRACT(value, '$.experiment') = '{experiment_name}'
        )
        """

        # Labelled samples to learn on
        if project.target is not None:
            query += f""" UNION ALL

            SELECT
                targets.{project.target.ts_field} AS ts,
                targets.{project.target.key_field} AS key,
                predictions.features,
                targets.{project.target.target_field} as target
            FROM {project.target_view_name} targets
            LEFT JOIN (
                SELECT
                    key,
                    JSON_EXTRACT(value, '$.features') AS features
                FROM messages
                WHERE topic = '{project.predictions_topic_name}'
                AND JSON_EXTRACT(value, '$.experiment') = '{experiment_name}'
            ) predictions ON
                targets.key = predictions.key
            """

        project.stream_processor.infra.create_view(
            name=dataset_name,
            query=f"""
            SELECT *
            FROM ({query})
            ORDER BY ts
            """,
        )
    else:
        raise RuntimeError(
            f"Unsupported stream processor protocol: {project.stream_processor.protocol}"
        )

    yield from (
        (
            dt.datetime.fromisoformat(r["ts"]),
            r["key"],
            json.loads(r["features"]),
            json.loads(r["target"]) if r["target"] else None,
        )
        for r in project.stream_processor.infra.stream_view(
            name=dataset_name, since=since
        )
    )


def do_progressive_learning(experiment_name: str):
    """

    Progressive learning is the act of intervealing predictions and learning. It is specific to
    online learning. This function first lists all the events that occurred since the last time
    checkpoint. These events constitute a chunk. The events are looped over, and the model does
    predictions and learns accordingly.

    Here's an example with three chunks:

    ```
    t1 k1 x1 --  =>  predict(x1) outputs p1
    t2 k2 x2 --  =>  predict(x2) outputs p2

    t3 k1 -- y1  =>  learn(x1, y1)
    t4 k3 x3 --  =>  predict(x3) outputs p3
    t5 k3 -- y3  =>  learn(x3, y3)

    t6 k2 -- y2  =>  learn(x2, y2)
    ```

    Each chunk is built and streamed thanks to iter_dataset.

    The idea is that this functions is run in the background repeatidly. This way, the models stay
    up-to-date, and predictions are made as soon as possible.

    """

    with db.session() as session:
        experiment = session.get(models.Experiment, experiment_name)
        project = experiment.project
        message_bus = project.message_bus
        model = experiment.get_model()
        feature_set = experiment.feature_set

    job = models.Job(experiment=experiment)

    # If this experiment has already done a prediction or a learning, then last_sample_ts will be
    # set. If not, then refer to the start_from_top parameter.
    since = experiment.last_sample_ts or (
        dt.datetime.min if experiment.start_from_top else experiment.created_at
    )

    for ts, key, features, label in iter_dataset(
        experiment_name=experiment.name,
        since=experiment.last_sample_ts or experiment.created_at,
    ):
        # LEARNING
        if label is not None:
            model.learn(features, label)
            job.n_learnings += 1
        # PREDICTING
        else:
            y_pred = model.predict(features)
            message_bus.infra.send(
                infra.Message(
                    topic=project.predictions_topic_name,
                    key=key,
                    value=json.dumps(
                        {
                            "project": project.name,
                            "experiment": experiment.name,
                            "prediction": y_pred,
                            "features": features,
                        }
                    ),
                )
            )
            job.n_predictions += 1
        # Bookkeeping
        experiment.last_sample_ts = ts

    with db.session() as session:
        experiment.set_model(model)
        session.add(experiment)
        session.add(job)
        session.commit()
        session.refresh(experiment)


def monitor_experiments(project_name: str):

    perf_view_name = f"performance_{project_name}"

    with db.session() as session:
        project = session.get(models.Project, project_name)
        stats = {
            experiment.name: {
                "n_learnings": sum(job.n_learnings for job in experiment.jobs),
                "n_predictions": sum(job.n_predictions for job in experiment.jobs),
            }
            for experiment in project.experiments
        }

    return stats
