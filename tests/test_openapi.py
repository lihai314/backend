"""OpenAPI 文档测试，验证元数据和路由路径正确性。"""

from fastapi.testclient import TestClient

from app.main import app


def test_openapi_metadata_and_paths() -> None:
    """验证 OpenAPI 文档包含正确的元数据和路由路径。"""
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
    assert "/api/v1/auth/register" in schema["paths"]
    assert "/api/v1/auth/login" in schema["paths"]
    assert "/api/v1/auth/logout" in schema["paths"]
    assert "/api/v1/users/me" in schema["paths"]
    assert "/api/v1/users/me/actions/change-password" in schema["paths"]
    assert "/health" not in schema["paths"]
