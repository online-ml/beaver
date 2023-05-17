import base64
import json
import functools
import collections
import pathlib
import urllib.parse
import dill
import pytest
from fastapi.testclient import TestClient
import sqlmodel
import sqlmodel.pool
import requests
from river import datasets, linear_model, preprocessing

from beaver.main import app
from beaver.db import engine, get_session
import beaver_sdk


@pytest.fixture(name="session")
def session_fixture():
    engine_ = sqlmodel.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=sqlmodel.pool.StaticPool,
    )
    sqlmodel.SQLModel.metadata.create_all(engine_)
    with sqlmodel.Session(engine_) as session:
        yield session


@pytest.fixture()
def client(session: sqlmodel.Session):
    """HACK: this is an override so that the Beaver SDK talks to the TestClient, instead of requests"""

    def get_session_override():
        yield session

    def request_override(*args, **kwargs):
        self, *args = args
        method, endpoint, *args = args
        endpoint = urllib.parse.urljoin(self.host, endpoint)
        r = client.request(method, endpoint, *args, **kwargs)
        r.raise_for_status()
        return r.json()

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    beaver_sdk.SDK.request = request_override
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def sdk(client):
    return beaver_sdk.Instance(host="")


@pytest.fixture()
def sqlite_mb_path():
    here = pathlib.Path(__file__).parent
    yield here / "message_bus.db"
    (here / "message_bus.db").unlink(missing_ok=True)


def test_phishing(sdk, sqlite_mb_path):
    sdk.message_bus.create(name="test_mb", protocol="SQLITE", url=str(sqlite_mb_path))
    sdk.stream_processor.create(
        name="test_sp", protocol="SQLITE", url=str(sqlite_mb_path)
    )
    sdk.job_runner.create(name="test_tr", protocol="SYNCHRONOUS")

    # Create a project
    project = sdk.project.create(
        name="phishing_project",
        task="BINARY_CLASSIFICATION",
        message_bus_name="test_mb",
        stream_processor_name="test_sp",
        job_runner_name="test_tr",
    )

    # Send 10 samples, without revealing answers
    message_bus = sdk.message_bus("test_mb")
    for i, (x, _) in enumerate(datasets.Phishing().take(10)):
        message_bus.send(topic="phishing_project_features", key=i, value=x)

    # Create a target
    project.target.set(
        query="SELECT key, created_at, value FROM messages WHERE topic = 'phishing_project_targets'",
        key_field="key",
        ts_field="created_at",
        value_field="value",
    )

    # Create a feature set
    project.feature_set.create(
        name="phishing_project_features",
        query="SELECT key, created_at, value FROM messages WHERE topic = 'phishing_project_features'",
        key_field="key",
        ts_field="created_at",
        value_field="value",
    )

    # Create an experiment
    model = preprocessing.StandardScaler() | linear_model.LogisticRegression()
    exp1 = project.experiment.create(
        name="phishing_experiment_1",
        feature_set_name="phishing_project_features",
        model=model,
        start_from_top=True,
    )

    # Create a second experiment
    model = preprocessing.StandardScaler() | linear_model.Perceptron()
    exp2 = project.experiment.create(
        name="phishing_experiment_2",
        feature_set_name="phishing_project_features",
        model=model,
        start_from_top=True,
    )

    # Check predictions were made
    state = project.state(with_experiments=True)
    assert state["experiments"]["phishing_experiment_1"]["n_predictions"] == 10
    assert state["experiments"]["phishing_experiment_1"]["n_learnings"] == 0
    assert state["experiments"]["phishing_experiment_1"]["accuracy"] == 0
    assert state["experiments"]["phishing_experiment_2"]["n_predictions"] == 10
    assert state["experiments"]["phishing_experiment_2"]["n_learnings"] == 0
    assert state["experiments"]["phishing_experiment_2"]["accuracy"] == 0

    # The first 10 samples were sent without labels -- send them in now
    for i, (_, y) in enumerate(datasets.Phishing().take(10)):
        message_bus.send(topic="phishing_project_targets", key=i, value=y)

    # We're using a synchronous task runner. Therefore, even though the labels have been sent, the
    # experiments are not automatically picking them up for learning. We have to explicitely make
    # them learn.
    exp1.start()
    exp2.start()

    # Check learning happened
    state = project.state(with_experiments=True)
    assert state["experiments"]["phishing_experiment_1"]["n_predictions"] == 10
    assert state["experiments"]["phishing_experiment_1"]["n_learnings"] == 10
    assert state["experiments"]["phishing_experiment_1"]["accuracy"] == 0.3
    assert state["experiments"]["phishing_experiment_2"]["n_predictions"] == 10
    assert state["experiments"]["phishing_experiment_2"]["n_learnings"] == 10
    assert state["experiments"]["phishing_experiment_2"]["accuracy"] == 0.3

    # Send next 5 samples, with labels
    for i, (x, y) in enumerate(datasets.Phishing().take(15)):
        if i < 10:
            continue
        message_bus.send(topic="phishing_project_features", key=i, value=x)
        message_bus.send(topic="phishing_project_targets", key=i, value=y)

    # Run the models
    exp1.start()
    exp2.start()

    # Check stats
    state = project.state(with_experiments=True)
    assert state["experiments"]["phishing_experiment_1"]["n_predictions"] == 15
    assert state["experiments"]["phishing_experiment_1"]["n_learnings"] == 15
    assert round(state["experiments"]["phishing_experiment_1"]["accuracy"], 3) == 0.467
    assert state["experiments"]["phishing_experiment_2"]["n_predictions"] == 15
    assert state["experiments"]["phishing_experiment_2"]["n_learnings"] == 15
    assert round(state["experiments"]["phishing_experiment_2"]["accuracy"], 3) == 0.533
