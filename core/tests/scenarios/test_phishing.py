import collections
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from api.main import app
from api.db import engine, get_session


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


def test_phishing(client: TestClient):

    # Create source
    response = client.post(
        "/api/sources",
        json={"name": "foo", "protocol": "DUMMY"},
    )
    assert response.status_code == 200
    assert len(client.get("/api/sources/").json()) == 1
    assert client.get("/api/sources/1").json()["name"] == "foo"
    assert client.get("/api/sources/1").json()["protocol"] == "DUMMY"
