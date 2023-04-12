from fastapi.testclient import TestClient

from beaver.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/docs")
    assert response.status_code == 200
