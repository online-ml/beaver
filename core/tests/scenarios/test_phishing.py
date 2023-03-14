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
        json={"name": "test", "protocol": "SQLITE", "url": str(sqlite_path)},
    )
    assert response.status_code == 200
    assert len(client.get("/api/message_bus/").json()) == 1
    assert client.get("/api/message_bus/test").json()["protocol"] == "SQLITE"


@pytest.fixture(name="create_stream_processor")
def create_stream_processor(client: TestClient, sqlite_path: pathlib.Path):

    # Create source
    response = client.post(
        "/api/stream_processor",
        json={"name": "test", "protocol": "SQLITE", "url": str(sqlite_path)},
    )
    assert response.status_code == 200
    assert len(client.get("/api/stream_processor/").json()) == 1
    assert client.get("/api/stream_processor/test").json()["protocol"] == "SQLITE"


def test_phishing(create_message_bus, create_stream_processor, client):

    # Send data, inteleaving features and targets
    for i, (x, y) in enumerate(datasets.Phishing().take(10)):
        assert (
            client.post(
                "/api/message_bus/test",
                json={
                    "topic": "features",
                    "key": f"phishing_{i}",
                    "value": json.dumps(x),
                },
            ).status_code
            == 201
        )
        assert (
            client.post(
                "/api/message_bus/test",
                json={"topic": "targets", "key": f"phishing_{i}", "value": str(y)},
            ).status_code
            == 201
        )
