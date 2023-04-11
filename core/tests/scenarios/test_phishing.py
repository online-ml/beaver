import base64
import json
import functools
import collections
import pathlib
import dill
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from river import datasets, linear_model, preprocessing, forest

from core.main import app
from core.db import engine, get_session


@pytest.fixture(name="session")
def session_fixture():

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
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
            "query": "SELECT key, created_at, value FROM messages WHERE topic = 'phishing_targets'",
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
        },
    )
    assert response.status_code == 201

    # Create a second experiment
    model = forest.AMFClassifier()
    model.learn = model.learn_one
    model.predict = model.predict_one
    response = client.post(
        "/api/experiment",
        json={
            "name": "phishing_experiment_2",
            "project_name": "phishing_project",
            "feature_set_name": "phishing_project_features",
            "model": base64.b64encode(dill.dumps(model)).decode("ascii"),
        },
    )
    assert response.status_code == 201

    # Check predictions were made
    response = client.get("/api/project/phishing_project").json()
    assert response["experiments"]["phishing_experiment_1"]["n_predictions"] == 10
    assert response["experiments"]["phishing_experiment_1"]["n_learnings"] == 0
    assert response["experiments"]["phishing_experiment_2"]["n_predictions"] == 10
    assert response["experiments"]["phishing_experiment_2"]["n_learnings"] == 0

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
    assert response["experiments"]["phishing_experiment_2"]["n_predictions"] == 10
    assert response["experiments"]["phishing_experiment_2"]["n_learnings"] == 10

    raise ValueError

    # TODO: move stream_processor.py methods to logic.py, basically an if-table based on stream processor and task
    # TODO: add message bus routes for sending features and labels

    # TODO: get model accuracy (worse possible at first)
    # TODO: send more unlabelled samples
    # TODO: send labels
    # TODO: get performance (should be better)
    # TODO: get best model
    # TODO: compare to doing it here

    # TODO: go through in old_logic.py, see what's missing (pausing/unpausing?é")
    # TODO: make an SDK!
