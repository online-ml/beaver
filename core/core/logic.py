import json
import fastapi
import sqlmodel as sqlm
from core import db, models, infra


def do_inference(experiment_name):

    with db.session() as session:
        experiment = session.get(models.Experiment, experiment_name)
        project = experiment.project
        message_bus = project.message_bus
        model = experiment.get_model()
        feature_set = experiment.feature_set
        feature_set.project.stream_processor

    for r in feature_set.stream(experiment.last_ts_seen):
        y_pred = model.predict(r["features"])
        message_bus.infra.send(
            infra.Message(
                topic="predictions",
                key=r["key"],
                value=json.dumps(
                    {
                        "project": project.name,
                        "experiment": experiment.name,
                        "prediction": y_pred,
                    }
                ),
            )
        )

    # processor.execute(
    #     f"""
    # CREATE VIEW learning_queue_{experiment_id} AS (
    #     SELECT
    #         t.{target.target_field} AS ground_truth,
    #         p.feature_set
    #     FROM {target.name} t
    #     INNER JOIN predictions_{experiment_id} p ON
    #         CAST(t.{target.key_field} as INTEGER) = CAST(p.key AS INTEGER)
    # )
    # """
    # )

    # model_obj = dill.loads(experiment.model_state)
    # model_last_dumped_at = dt.datetime.now()
    # n_samples_trained_on = 0

    # for sample in processor.stream(f"learning_queue_{experiment_id}"):
    #     model_obj.learn(sample["feature_set"], sample["ground_truth"])
    #     n_samples_trained_on += 1

    #     # Dump models every 30 seconds
    #     if (now := dt.datetime.now()) - model_last_dumped_at > dt.timedelta(
    #         seconds=experiment.sync_seconds
    #     ):
    #         with db.session() as session:
    #             experiment.model_state = dill.dumps(model_obj)
    #             experiment.n_samples_trained_on += n_samples_trained_on
    #             n_samples_trained_on = 0
    #             session.add(experiment)
    #             session.commit()
    #             model_last_dumped_at = now
