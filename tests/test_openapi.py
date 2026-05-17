from fastapi.testclient import TestClient

from app.main import app


def test_openapi_metadata_and_paths() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"] == {
        "title": "Backend API",
        "description": "Backend service API",
        "version": "0.1.0",
    }
    assert "/api/v1/health" in schema["paths"]
    assert "/health" not in schema["paths"]
