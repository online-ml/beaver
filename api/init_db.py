import json
import dill
import kafka
import sqlmodel as sqlm
from river import datasets, linear_model, preprocessing
from api import db
from api import experiments
from api import feature_sets
from api import models
from api import processors
from api import runners
from api import sinks
from api import sources
from api import tasks
from api import targets


if __name__ == "__main__":

    # Recreate database
    sqlm.SQLModel.metadata.drop_all(db.engine)
    sqlm.SQLModel.metadata.create_all(db.engine)

    # Create default infrastructure
    with db.session() as session:

        # SOURCES

        session.add(
            sources.Source(
                name="Default source", protocol="Redpanda", url="redpanda:29092"
            )
        )
        while True:
            # Keep trying to connect to the broker
            try:
                message_bus_admin = kafka.admin.KafkaAdminClient(
                    bootstrap_servers=["redpanda:29092"]
                )
                break
            except kafka.errors.NodeNotReadyError:
                print("Waiting for Redpanda...")
                ...

        for topic_name in ["examples-phishing"]:
            try:
                message_bus_admin.delete_topics([topic_name])
            except kafka.errors.UnknownTopicOrPartitionError:
                ...
        message_bus = kafka.KafkaProducer(
            bootstrap_servers=["redpanda:29092"],
            key_serializer=str.encode,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        for i, (x, y) in enumerate(datasets.Phishing()):
            message_bus.send(
                topic="examples-phishing",
                key=str(i),
                value={"features": x, "target": y},
            )

        # PROCESSORS

        processor = processors.Processor(
            name="Default processor",
            protocol="Materialize",
            url="postgresql://materialize@materialize:6875/materialize?sslmode=disable",
        )
        session.add(processor)
        session.commit()
        session.refresh(processor)

        # HACK
        processor.execute(
            """
        DROP VIEW IF EXISTS performance_1;
        DROP VIEW IF EXISTS learning_queue_1;
        DROP VIEW IF EXISTS phishing_target;
        DROP VIEW IF EXISTS phishing_features;
        DROP VIEW IF EXISTS phishing;
        DROP SOURCE IF EXISTS examples_phishing;
        """
        )

        # RUNNERS

        runner = runners.Runner(
            name="Default runner",
            protocol="Celery on Redis",
            url="redis://redis:6379/0",
        )
        session.add(runner)
        session.commit()
        session.refresh(runner)

        # SINKS

        sink = sinks.Sink(
            name="Default sink", protocol="Redpanda", url="redpanda:29092"
        )
        session.add(sink)

        topic_name = "predictions"
        try:
            message_bus_admin.delete_topics([topic_name])
        except kafka.errors.UnknownTopicOrPartitionError:
            ...
        topic = kafka.admin.NewTopic(
            name=topic_name, num_partitions=3, replication_factor=1
        )
        message_bus_admin.create_topics([topic])

        # MODELS

        model_obj = preprocessing.StandardScaler() | linear_model.LogisticRegression()
        model_obj.learn = model_obj.learn_one
        model_obj.predict = model_obj.predict_proba_one
        model = models.Model(
            name="Logistic regression",
            task=tasks.TaskEnum.binary_clf,
            content=dill.dumps(model_obj),
        )
        session.add(model)
        session.commit()
        session.refresh(model)

        # FEATURES

        feature_set = feature_sets.FeatureSet(
            name="phishing_features",
            query="""CREATE MATERIALIZED SOURCE examples_phishing
FROM KAFKA BROKER 'redpanda:29092' TOPIC 'examples-phishing'
    KEY FORMAT BYTES
    VALUE FORMAT BYTES
    INCLUDE KEY AS row_id;

CREATE VIEW phishing AS (
    SELECT
        CAST(CONVERT_FROM(row_id, 'utf8') AS INTEGER) AS row_id,
        (CAST(CONVERT_FROM(data, 'utf8') AS JSONB) ->> 'features')::JSONB AS features,
        (CAST(CONVERT_FROM(data, 'utf8') AS JSONB) ->> 'target')::JSONB AS target
    FROM examples_phishing
);

CREATE VIEW phishing_features AS (
    SELECT
        row_id,
        CAST(features -> 'age_of_domain' AS INTEGER) AS age_of_domain,
        CAST(features -> 'anchor_from_other_domain' AS FLOAT) AS anchor_from_other_domain,
        CAST(features -> 'empty_server_form_handler' AS FLOAT) AS empty_server_form_handler,
        CAST(features -> 'https' AS FLOAT) AS https,
        CAST(features -> 'ip_in_url' AS INTEGER) AS ip_in_url,
        CAST(features -> 'is_popular' AS FLOAT) AS is_popular,
        CAST(features -> 'long_url' AS FLOAT) AS long_url,
        CAST(features -> 'popup_window' AS FLOAT) AS popup_window,
        CAST(features -> 'request_from_other_domain' AS FLOAT) AS request_from_other_domain
    FROM phishing
)""",
            key_field="row_id",
            processor_id=processor.id,
        ).create(session)

        # TARGETS

        target = targets.Target(
            name="phishing_target",
            query="""CREATE VIEW phishing_target AS (
    SELECT
        row_id,
        CAST(target AS BOOL) AS is_phishing
    FROM phishing
)""",
            key_field="row_id",
            target_field="is_phishing",
            task=tasks.TaskEnum.binary_clf,
            processor_id=processor.id,
        ).create(session)

        # EXPERIMENTS

        try:
            message_bus_admin.delete_topics(["predictions_1"])
        except kafka.errors.UnknownTopicOrPartitionError:
            ...

        exp = experiments.Experiment(
            name="Phishing log reg experiment",
            feature_set_id=feature_set.id,
            target_id=target.id,
            model_id=model.id,
            runner_id=runner.id,
            sink_id=sink.id,
        )
        exp.create(session)

        session.commit()
