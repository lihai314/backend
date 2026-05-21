"""健康检查端点测试，验证存活探针响应结构。"""

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    """验证 GET /api/v1/health 返回预期的响应结构和数据。"""
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "code": "OK",
        "message": "ok",
        "data": {"status": "healthy"},
    }
