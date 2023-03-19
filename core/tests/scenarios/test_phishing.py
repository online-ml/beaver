import json
import functools
import collections
import pathlib
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from river import datasets

from core.main import app
from core.db import engine, get_session


@pytest.fixture(name="session")
def session_fixture():

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sqlite_path")
def sqlite_path():
    here = pathlib.Path(__file__).parent
    yield here / "test.db"
    (here / "test.db").unlink(missing_ok=True)


@pytest.fixture(name="create_message_bus")
def create_message_bus(client: TestClient, sqlite_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/message-bus",
        json={"name": "test_mb", "protocol": "SQLITE", "url": str(sqlite_path)},
    )
    assert response.status_code == 201
    assert len(client.get("/api/message-bus/").json()) == 1
    assert client.get("/api/message-bus/test_mb").json()["protocol"] == "SQLITE"


@pytest.fixture(name="create_stream_processor")
def create_stream_processor(client: TestClient, sqlite_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/stream-processor",
        json={"name": "test_sp", "protocol": "SQLITE", "url": str(sqlite_path)},
    )
    assert response.status_code == 201
    assert len(client.get("/api/stream-processor/").json()) == 1
    assert client.get("/api/stream-processor/test_sp").json()["protocol"] == "SQLITE"


@pytest.fixture(name="create_task_runner")
def create_task_runner(client: TestClient, sqlite_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/task-runner",
        json={"name": "test_tr", "protocol": "FASTAPI_BACKGROUND_TASKS"},
    )
    assert response.status_code == 201
    assert len(client.get("/api/task-runner/").json()) == 1
    assert (
        client.get("/api/task-runner/test_tr").json()["protocol"]
        == "FASTAPI_BACKGROUND_TASKS"
    )


def test_phishing(
    create_message_bus, create_stream_processor, create_task_runner, client
):

    # Send data, inteleaving features and targets
    for i, (x, y) in enumerate(datasets.Phishing().take(10)):
        assert (
            client.post(
                "/api/message-bus/test_mb",
                json={
                    "topic": "phishing_features",
                    "key": f"phishing_{i}",
                    "value": json.dumps(x),
                },
            ).status_code
            == 201
        )
        assert (
            client.post(
                "/api/message-bus/test_mb",
                json={
                    "topic": "phishing_targets",
                    "key": f"phishing_{i}",
                    "value": str(y),
                },
            ).status_code
            == 201
        )

    # Create a project
    response = client.post(
        "/api/project",
        json={
            "name": "phishing_project",
            "task": "BINARY_CLASSIFICATION",
            "task_runner_name": "test_tr",
            "stream_processor_name": "test_sp",
            "sink_message_bus_name": "test_mb",
        },
    )
    assert response.status_code == 201

    # Create a target
    response = client.post(
        "/api/target",
        json={
            "project_name": "phishing_project",
            "query": "SELECT key, value FROM messages WHERE topic = 'phishing_targets'",
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
            "name": "phishing_features_1",
            "project_name": "phishing_project",
            "query": "SELECT key, value FROM messages WHERE topic = 'phishing_features'",
            "key_field": "key",
            "ts_field": "created_at",
        },
    )
    assert response.status_code == 201

    # TODO: run the above in a notebook to continue testing
    # TODO: create an experiment (includes the model, simpler like that)
    # TODO: create a second experiment
    # TODO: monitor, thanks to the project's message bus for sending predictions and stream processor for measuring performance
    # TODO: make an SDK!
