import json
import fastapi
import sqlmodel as sqlm
from core import db, enums, models, infra


def iter_dataset(experiment_name, since):

    dataset_name = f"{experiment_name}_dataset"

    with db.session() as session:
        experiment = session.get(models.Experiment, experiment_name)
        project = experiment.project
        project.stream_processor
        experiment.feature_set
        project.target

    if project.stream_processor.protocol == enums.StreamProcessor.sqlite.value:
        project.stream_processor.infra.create_view(
            name=dataset_name,
            query=f"""
            SELECT
                features.{experiment.feature_set.ts_field} AS ts,
                features.{experiment.feature_set.key_field} AS key,
                IIF(predictions.key IS NULL, features.value, predictions.features) AS features,
                IIF(predictions.key IS NULL, NULL, targets.value) AS target
            FROM {experiment.feature_set.name} features
            LEFT JOIN {project.target_view_name} targets ON
                features.key = targets.key
            LEFT JOIN (
                SELECT
                    key,
                    JSON_EXTRACT(value, '$.features') AS features
                FROM messages
                WHERE topic = '{project.predictions_topic_name}'
                AND JSON_EXTRACT(value, '$.experiment') = '{experiment_name}'
            ) predictions ON
                features.key = predictions.key
            ORDER BY 1
            """,
        )
    else:
        raise RuntimeError(
            f"Unsupported stream processor protocol: {project.stream_processor.protocol}"
        )

    yield from (
        (
            r["key"],
            json.loads(r["features"]),
            json.loads(r["target"]) if r["target"] else None,
        )
        for r in project.stream_processor.infra.stream_view(
            name=dataset_name, since=since
        )
    )


def do_progressive_learning(experiment_name):

    with db.session() as session:
        experiment = session.get(models.Experiment, experiment_name)
        project = experiment.project
        message_bus = project.message_bus
        model = experiment.get_model()
        feature_set = experiment.feature_set

    job = models.Job(experiment=experiment)

    for key, features, label in iter_dataset(
        experiment_name=experiment.name, since=experiment.last_sample_ts
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
