import datetime as dt
import json
import functools
import pathlib
import pytest
import sqlmodel
from core import enums, infra, logic, models


@functools.cache
@pytest.fixture(name="session")
def session_fixture():
    engine = sqlmodel.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=sqlmodel.pool.StaticPool,
    )
    sqlmodel.SQLModel.metadata.create_all(engine)
    with sqlmodel.Session(engine) as session:
        return session


@pytest.fixture(name="sqlite_mb_path")
def sqlite_mb_path():
    here = pathlib.Path(__file__).parent
    yield here / "message_bus.db"
    (here / "message_bus.db").unlink(missing_ok=True)


@pytest.fixture(name="message_bus")
def sqlite_message_bus(session, sqlite_mb_path: pathlib.Path):
    return models.MessageBus(
        name="sqlite_message_bus",
        protocol=enums.MessageBus.sqlite,
        url=str(sqlite_mb_path),
    ).save(session)


@pytest.fixture(name="stream_processor")
def sqlite_stream_processor(session, sqlite_mb_path: pathlib.Path):
    return models.StreamProcessor(
        name="sqlite_stream_processor",
        protocol=enums.StreamProcessor.sqlite,
        url=str(sqlite_mb_path),
    ).save(session)


@pytest.fixture(name="job_runner")
def synchronous_processor(session, sqlite_mb_path: pathlib.Path):
    return models.JobRunner(
        name="synchronous_processor", protocol=enums.JobRunner.synchronous
    ).save(session)


def test_iter_dataset(session, message_bus, stream_processor, job_runner):
    """Test the iter_dataset function using different message buses and stream processors."""

    project = models.Project(
        name="test_project",
        task=enums.Task.regression,
        message_bus_name=message_bus.name,
        stream_processor_name=stream_processor.name,
        job_runner_name=job_runner.name,
    )
    project.save(session)

    # Create a feature set
    if project.stream_processor.protocol == enums.StreamProcessor.sqlite:
        fs_query = f"SELECT key, created_at, value FROM messages WHERE topic = '{project.name}_features'"
    else:
        raise RuntimeError(
            f"Unsupported stream processor protocol: {project.stream_processor.protocol}"
        )
    feature_set = models.FeatureSet(
        name=f"{project.name}_features",
        project_name=project.name,
        query=fs_query,
        key_field="key",
        ts_field="created_at",
        features_field="value",
    )
    feature_set.save(session)
    project.stream_processor.infra.create_view(
        name=feature_set.name, query=feature_set.query
    )

    # Create a target
    if project.stream_processor.protocol == enums.StreamProcessor.sqlite:
        target_query = f"SELECT key, created_at, value FROM messages WHERE topic = '{project.name}_targets'"
    else:
        raise RuntimeError(
            f"Unsupported stream processor protocol: {project.stream_processor.protocol}"
        )
    target = models.Target(
        project_name=project.name,
        query=target_query,
        key_field="key",
        ts_field="created_at",
        target_field="value",
    )
    target.save(session)
    project.stream_processor.infra.create_view(
        name=project.target_view_name, query=target.query
    )

    # Send data in a particular order
    events = [
        (dt.datetime(2000, 1, 1), "k1", {}, None),
        (dt.datetime(2000, 1, 2), "k2", {}, None),
        (dt.datetime(2000, 1, 3), "k1", None, 1),
        (dt.datetime(2000, 1, 4), "k3", {}, None),
        (dt.datetime(2000, 1, 5), "k3", None, 1),
        (dt.datetime(2000, 1, 6), "k2", None, 1),
    ]
    for ts, key, features, target in events:
        message = infra.Message(
            topic=f"{project.name}_features"
            if features is not None
            else f"{project.name}_targets",
            key=key,
            created_at=ts,
            value=json.dumps(features if features is not None else target),
        )
        message_bus.infra.send(message)

    # Create an experiment
    experiment = models.Experiment(
        name="test_experiment",
        project_name=project.name,
        model="doesn't matter",
        feature_set_name=feature_set.name,
    )
    experiment.save(session)

    samples = list(
        logic.iter_dataset_for_experiment(
            experiment_name=experiment.name,
            since=dt.datetime(1999, 12, 31),
            session=session,
        )
    )
    assert len(samples) == 6

    samples = list(
        logic.iter_dataset_for_experiment(
            experiment_name=experiment.name,
            since=dt.datetime(2000, 1, 4),
            session=session,
        )
    )
    assert len(samples) == 2
