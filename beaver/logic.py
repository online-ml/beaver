import datetime as dt
import json
import uuid
import fastapi
import sqlmodel as sqlm
from beaver import db, enums, models, infra


def iter_dataset_for_experiment(
    experiment: models.Experiment, since: dt.datetime, session: sqlm.Session = None
):

    dataset_name = f"{experiment.name}_dataset"

    with (session or db.session()) as session:
        project = session.get(models.Project, experiment.project_name)
        project.stream_processor
        feature_set = session.get(models.FeatureSet, experiment.feature_set_name)
        project.target

    if project.stream_processor.protocol == enums.StreamProcessor.sqlite.value:

        # Unlabelled samples that need predicting
        query = f"""
        SELECT
            features.{feature_set.ts_field} AS ts,
            features.{feature_set.key_field} AS key,
            features.{feature_set.value_field} AS features,
            NULL as target
        FROM {feature_set.name} features
        WHERE features.{feature_set.key_field} NOT IN (
            SELECT key
            FROM messages
            WHERE topic = '{project.predictions_topic_name}'
            AND JSON_EXTRACT(value, '$.experiment') = '{experiment.name}'
        )
        """

        # Labelled samples to learn on
        if project.target is not None and experiment.can_learn:
            query += f""" UNION ALL

            SELECT
                targets.{project.target.ts_field} AS ts,
                targets.{project.target.key_field} AS key,
                predictions.features,
                targets.{project.target.value_field} as target
            FROM {project.target_view_name} targets
            LEFT JOIN (
                SELECT
                    JSON_EXTRACT(value, '$.key') AS key,
                    JSON_EXTRACT(value, '$.features') AS features
                FROM messages
                WHERE topic = '{project.predictions_topic_name}'
                AND JSON_EXTRACT(value, '$.experiment') = '{experiment.name}'
            ) predictions ON
                targets.key = predictions.key
            """

        query = f"""
        SELECT *
        FROM ({query})
        ORDER BY ts
        """

        project.stream_processor.infra.create_view(
            name=dataset_name,
            query=query
        )

        yield from (
            (
                dt.datetime.fromisoformat(r["ts"]),
                r["key"],
                json.loads(r["features"]) if r["features"] else None,
                json.loads(r["target"]) if r["target"] else None,
            )
            for r in project.stream_processor.infra.stream_view(
                name=dataset_name, since=since
            )
        )

    elif project.stream_processor.protocol == enums.StreamProcessor.materialize.value:

        query = f"""
        SELECT
            features.{feature_set.ts_field} AS ts,
            features.{feature_set.key_field} AS key,
            features.{feature_set.value_field} AS features,
            NULL as target
        FROM {feature_set.name} features
        WHERE features.{feature_set.key_field} NOT IN (
            SELECT key
            FROM {project.predictions_topic_name}
            AND value['experiment'] = '{experiment.name}'
        )
        """

        query = f"""
        SELECT *
        FROM ({query})
        ORDER BY ts
        """

        project.stream_processor.infra.create_view(
            name=dataset_name,
            query=query
        )

        yield from (
            (
                r["ts"],
                r["key"],
                r["features"],
                r["target"]
            )
            for r in project.stream_processor.infra.stream_view(
                name=dataset_name, since=since
            )
        )

    else:
        raise RuntimeError(
            f"Unsupported stream processor protocol: {project.stream_processor.protocol}"
        )


def do_progressive_learning(experiment: models.Experiment):
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

    Each chunk is built and streamed thanks to iter_dataset_for_experiment.

    The idea is that this functions is run in the background repeatidly. This way, the models stay
    up-to-date, and predictions are made as soon as possible.

    """

    with db.session() as session:
        project = session.get(models.Project, experiment.project_name)
        message_bus = project.message_bus
        model = experiment.get_model()
        feature_set = session.get(models.FeatureSet, experiment.feature_set_name)

    job = models.Job(experiment=experiment)

    # If this experiment has already done a prediction or a learning, then last_sample_ts will be
    # set. If not, then refer to the start_from_top parameter.
    since = experiment.last_sample_ts or (
        dt.datetime.min if experiment.start_from_top else experiment.created_at
    )

    # When the model learns, it uses the same features that were used for making a prediction. This
    # is by design, to prevent leakage. However, if a prediction has not been made yet, then labels
    # won't be accompanied with the relevant features. Therefore, we keep them in memory so they
    # can be used for learning.
    features_used_for_predicting: dict[str, dict] = {}

    for ts, key, features, label in iter_dataset_for_experiment(
        experiment=experiment, since=since
    ):
        # LEARNING
        if label is not None:
            model.learn(features or features_used_for_predicting[key], label)
            job.n_learnings += 1
        # PREDICTING
        else:
            y_pred = model.predict(features)

            # Cast to appropriate type
            if project.task == enums.Task.binary_clf.value:
                y_pred = bool(y_pred)

            prediction_event = infra.Message(
                topic=project.predictions_topic_name,
                key=str(uuid.uuid4()),
                value=json.dumps(
                    {
                        "key": key,
                        "project": project.name,
                        "experiment": experiment.name,
                        "prediction": json.dumps(y_pred),
                        "features": json.dumps(features),
                    }
                ),
            )
            message_bus.infra.send(prediction_event)
            job.n_predictions += 1
            features_used_for_predicting[key] = features
        # Bookkeeping
        experiment.last_sample_ts = ts

    with db.session() as session:
        experiment.set_model(model)
        session.add(experiment)
        session.add(job)
        session.commit()
        session.refresh(experiment)


def do_progressive_learning_from_experiment_name(experiment_name: str):
    with db.session() as session:
        experiment = session.get(models.Experiment, experiment_name)
    do_progressive_learning(experiment)


def get_experiment_performance_for_project(project_name: str) -> dict:

    performance_view_name = f"{project_name}_performance"

    with db.session() as session:
        project = session.get(models.Project, project_name)
        project.stream_processor
        project.target

    if project.target is None:
        return {}

    if project.stream_processor.protocol == enums.StreamProcessor.sqlite.value:
        if project.task == enums.Task.binary_clf.value:
            query = f"""
            SELECT
                experiment,
                COALESCE((tn + tp) / NULLIF(n, 0), 0) AS accuracy,
                COALESCE(tp / NULLIF((tp + fn), 0), 0) AS recall,
                COALESCE(tp / NULLIF((tp + fp), 0), 0) AS precision
            FROM (
                SELECT
                    predictions.experiment,
                    CAST(COUNT(*) FILTER (WHERE y_pred AND y_true) AS REAL) AS tp,
                    CAST(COUNT(*) FILTER (WHERE y_pred AND NOT y_true) AS REAL) AS fp,
                    CAST(COUNT(*) FILTER (WHERE NOT y_pred AND NOT y_true) AS REAL) AS tn,
                    CAST(COUNT(*) FILTER (WHERE NOT y_pred AND y_true) AS REAL) AS fn,
                    CAST(COUNT(*) AS REAL) AS n
                FROM (
                    SELECT
                        JSON_EXTRACT(value, '$.key') AS key,
                        JSON_EXTRACT(value, '$.prediction') = 'true' AS y_pred,
                        JSON_EXTRACT(value, '$.experiment') AS experiment
                    FROM messages
                    WHERE topic = '{project.predictions_topic_name}'
                ) predictions
                LEFT JOIN (
                    SELECT
                        {project.target.key_field} AS key,
                        {project.target.value_field} = 'true' as y_true
                    FROM {project.target_view_name}
                ) targets ON
                    targets.key = predictions.key
                GROUP BY 1
            )
            """
        elif project.task == enums.Task.regression.value:
            query = f"""
            SELECT
                experiment,
                AVG(POW(y_true - y_pred, 2)) AS mse,
                AVG(ABS(y_true - y_pred)) AS mae
            FROM (
                SELECT
                    JSON_EXTRACT(value, '$.key') AS key,
                    CAST(JSON_EXTRACT(value, '$.prediction') AS FLOAT) AS y_pred,
                    JSON_EXTRACT(value, '$.experiment') AS experiment
                FROM messages
                WHERE topic = '{project.predictions_topic_name}'
            ) predictions
            LEFT JOIN (
                SELECT
                    {project.target.key_field} AS key,
                    {project.target.value_field} as y_true
                FROM {project.target_view_name}
            ) targets ON
                targets.key = predictions.key
            GROUP BY 1
            """
        else:
            raise RuntimeError(
                f"Unsupported task {project.task} for stream processor protocol {project.stream_processor.protocol}"
            )
        project.stream_processor.infra.create_view(
            name=performance_view_name, query=query
        )

    elif project.stream_processor.protocol == enums.StreamProcessor.materialize.value:
        ...

    else:
        raise RuntimeError(
            f"Unsupported stream processor protocol: {project.stream_processor.protocol}"
        )

    return {
        r.pop("experiment"): r
        for r in project.stream_processor.infra.stream_view(name=performance_view_name)
    }


def monitor_experiments(project_name: str):

    experiment_performance = get_experiment_performance_for_project(project_name)

    with db.session() as session:
        project = session.get(models.Project, project_name)
        stats = {
            experiment.name: {
                "n_learnings": sum(job.n_learnings for job in experiment.jobs),
                "n_predictions": sum(job.n_predictions for job in experiment.jobs),
                **experiment_performance.get(experiment.name, {}),
            }
            for experiment in project.experiments
        }

    return stats
