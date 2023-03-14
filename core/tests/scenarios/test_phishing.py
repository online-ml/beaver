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
        "/api/message_bus",
        json={"name": "test-mb", "protocol": "SQLITE", "url": str(sqlite_path)},
    )
    assert response.status_code == 201
    assert len(client.get("/api/message_bus/").json()) == 1
    assert client.get("/api/message_bus/test-mb").json()["protocol"] == "SQLITE"


@pytest.fixture(name="create_stream_processor")
def create_stream_processor(client: TestClient, sqlite_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/stream_processor",
        json={"name": "test-sp", "protocol": "SQLITE", "url": str(sqlite_path)},
    )
    assert response.status_code == 201
    assert len(client.get("/api/stream_processor/").json()) == 1
    assert client.get("/api/stream_processor/test-sp").json()["protocol"] == "SQLITE"


def test_phishing(create_message_bus, create_stream_processor, client):

    # Send data, inteleaving features and targets
    for i, (x, y) in enumerate(datasets.Phishing().take(10)):
        assert (
            client.post(
                "/api/message_bus/test-mb",
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
                "/api/message_bus/test-mb",
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
            "name": "phishing-project",
            "task": "BINARY_CLASSIFICATION",
            "stream_processor_name": "test-sp",
            "sink_message_bus_name": "test-mb",
        },
    )
    assert response.status_code == 201

    # Create a target
    response = client.post(
        "/api/target",
        json={
            "project_name": "phishing-project",
            "query": "SELECT key, value FROM messages WHERE topic = 'phishing_targets'",
            "key_field": "key",
            "target_field": "value",
        },
    )
    assert response.status_code == 201

    # Create a features set
    response = client.post(
        "/api/feature_set",
        json={
            "name": "phishing-features-1",
            "project_name": "phishing-project",
            "query": "SELECT key, value FROM messages WHERE topic = 'phishing_features'",
            "key_field": "key",
        },
    )
    assert response.status_code == 201

    # TODO: run the above in a notebook to continue testing
    # TODO: create a runner before creating the project, feed it to the project
    # TODO: create an experiment (includes the model, simpler like that)
    # TODO: create a second experiment
    # TODO: monitor, thanks to the project's message bus for sending predictions and stream processor for measuring performance
