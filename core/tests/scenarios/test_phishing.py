import base64
import json
import functools
import collections
import pathlib
import dill
import pytest
from fastapi.testclient import TestClient
import sqlmodel
import sqlmodel.pool
from river import datasets, linear_model, preprocessing

from core.main import app
from core.db import engine, get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = sqlmodel.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=sqlmodel.pool.StaticPool,
    )
    sqlmodel.SQLModel.metadata.create_all(engine)
    with sqlmodel.Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: sqlmodel.Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sqlite_mb_path")
def sqlite_mb_path():
    here = pathlib.Path(__file__).parent
    yield here / "message_bus.db"
    (here / "message_bus.db").unlink(missing_ok=True)


@pytest.fixture(name="create_message_bus")
def create_message_bus(client: TestClient, sqlite_mb_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/message-bus",
        json={"name": "test_mb", "protocol": "SQLITE", "url": str(sqlite_mb_path)},
    )
    assert response.status_code == 201
    assert len(client.get("/api/message-bus/").json()) == 1
    assert client.get("/api/message-bus/test_mb").json()["protocol"] == "SQLITE"


@pytest.fixture(name="create_stream_processor")
def create_stream_processor(client: TestClient, sqlite_mb_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/stream-processor",
        json={"name": "test_sp", "protocol": "SQLITE", "url": str(sqlite_mb_path)},
    )
    assert response.status_code == 201
    assert len(client.get("/api/stream-processor/").json()) == 1
    assert client.get("/api/stream-processor/test_sp").json()["protocol"] == "SQLITE"


@pytest.fixture(name="create_job_runner")
def create_job_runner(client: TestClient, sqlite_mb_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/task-runner",
        json={"name": "test_tr", "protocol": "SYNCHRONOUS"},
    )
    assert response.status_code == 201
    assert len(client.get("/api/task-runner/").json()) == 1
    assert client.get("/api/task-runner/test_tr").json()["protocol"] == "SYNCHRONOUS"


def test_phishing(
    create_message_bus, create_stream_processor, create_job_runner, client
):

    # Create a project
    response = client.post(
        "/api/project",
        json={
            "name": "phishing_project",
            "task": "BINARY_CLASSIFICATION",
            "message_bus_name": "test_mb",
            "stream_processor_name": "test_sp",
            "job_runner_name": "test_tr",
        },
    )
    assert response.status_code == 201

    # Send 10 samples, without revealing answers
    for i, (x, _) in enumerate(datasets.Phishing().take(10)):
        assert (
            client.post(
                "/api/message-bus/test_mb",  # TODO: derive message bus through project
                json={
                    "topic": "phishing_project_features",
                    "key": str(i),
                    "value": json.dumps(x),
                },
            ).status_code
            == 201
        )

    # Create a target
    response = client.post(
        "/api/target",
        json={
            "project_name": "phishing_project",
            "query": "SELECT key, created_at, value FROM messages WHERE topic = 'phishing_project_targets'",
            "key_field": "key",
            "ts_field": "created_at",
            "target_field": "value",
        },
    )
    assert response.status_code == 201

    # Create a feature set
    response = client.post(
        "/api/feature-set",
        json={
            "name": "phishing_project_features",
            "project_name": "phishing_project",
            "query": "SELECT key, created_at, value FROM messages WHERE topic = 'phishing_project_features'",
            "key_field": "key",
            "ts_field": "created_at",
            "features_field": "value",
        },
    )
    assert response.status_code == 201

    # Create an experiment
    model = preprocessing.StandardScaler() | linear_model.LogisticRegression()
    model.learn = model.learn_one
    model.predict = model.predict_one
    response = client.post(
        "/api/experiment",
        json={
            "name": "phishing_experiment_1",
            "project_name": "phishing_project",
            "feature_set_name": "phishing_project_features",
            "model": base64.b64encode(dill.dumps(model)).decode("ascii"),
            "start_from_top": True,
        },
    )
    assert response.status_code == 201

    # Create a second experiment
    model = preprocessing.StandardScaler() | linear_model.Perceptron()
    model.learn = model.learn_one
    model.predict = model.predict_one
    response = client.post(
        "/api/experiment",
        json={
            "name": "phishing_experiment_2",
            "project_name": "phishing_project",
            "feature_set_name": "phishing_project_features",
            "model": base64.b64encode(dill.dumps(model)).decode("ascii"),
            "start_from_top": True,
        },
    )
    assert response.status_code == 201

    # Check predictions were made
    response = client.get("/api/project/phishing_project").json()
    assert response["experiments"]["phishing_experiment_1"]["n_predictions"] == 10
    assert response["experiments"]["phishing_experiment_1"]["n_learnings"] == 0
    assert response["experiments"]["phishing_experiment_1"]["accuracy"] == 0
    assert response["experiments"]["phishing_experiment_2"]["n_predictions"] == 10
    assert response["experiments"]["phishing_experiment_2"]["n_learnings"] == 0
    assert response["experiments"]["phishing_experiment_2"]["accuracy"] == 0

    # The first 10 samples were sent without labels -- send them in now
    for i, (_, y) in enumerate(datasets.Phishing().take(10)):
        assert (
            client.post(
                "/api/message-bus/test_mb",
                json={
                    "topic": "phishing_project_targets",
                    "key": str(i),
                    "value": json.dumps(y),
                },
            ).status_code
            == 201
        )

    # We're using a synchronous task runner. Therefore, even though the labels have been sent, the
    # experiments are not automatically picking them up for learning. We have to explicitely make
    # them learn.
    response = client.put("/api/experiment/phishing_experiment_1/unpause")
    assert response.status_code == 200
    response = client.put("/api/experiment/phishing_experiment_2/unpause")
    assert response.status_code == 200

    # Check learning happened
    response = client.get("/api/project/phishing_project").json()
    assert response["experiments"]["phishing_experiment_1"]["n_predictions"] == 10
    assert response["experiments"]["phishing_experiment_1"]["n_learnings"] == 10
    assert response["experiments"]["phishing_experiment_1"]["accuracy"] == 0.3
    assert response["experiments"]["phishing_experiment_2"]["n_predictions"] == 10
    assert response["experiments"]["phishing_experiment_2"]["n_learnings"] == 10
    assert response["experiments"]["phishing_experiment_2"]["accuracy"] == 0.3

    # Send next 5 samples, with labels
    for i, (x, y) in enumerate(datasets.Phishing().take(15)):
        if i < 10:
            continue
        assert (
            client.post(
                "/api/message-bus/test_mb",
                json={
                    "topic": "phishing_project_features",
                    "key": str(i),
                    "value": json.dumps(x),
                },
            ).status_code
            == 201
        )
        assert (
            client.post(
                "/api/message-bus/test_mb",
                json={
                    "topic": "phishing_project_targets",
                    "key": str(i),
                    "value": json.dumps(y),
                },
            ).status_code
            == 201
        )

    # Run the models
    response = client.put("/api/experiment/phishing_experiment_1/unpause")
    assert response.status_code == 200
    response = client.put("/api/experiment/phishing_experiment_2/unpause")
    assert response.status_code == 200

    # Check stats
    response = client.get("/api/project/phishing_project").json()
    assert response["experiments"]["phishing_experiment_1"]["n_predictions"] == 15
    assert response["experiments"]["phishing_experiment_1"]["n_learnings"] == 15
    assert (
        round(response["experiments"]["phishing_experiment_1"]["accuracy"], 3) == 0.467
    )
    assert response["experiments"]["phishing_experiment_2"]["n_predictions"] == 15
    assert response["experiments"]["phishing_experiment_2"]["n_learnings"] == 15
    assert (
        round(response["experiments"]["phishing_experiment_2"]["accuracy"], 3) == 0.533
    )

    # TODO: go through in old_logic.py, see what's missing (pausing/unpausing?")
    # TODO: revisit API interface, decouple it from models (add message bus routes for sending features and labels?)
    # TODO: make an SDK!

    # TODO: finish tests in test_logic.py

    # TODO: test scenario with two batch models that can't learn
