"""全局异常处理器测试，验证各类异常均返回统一 JSON 响应格式。"""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.exception_handlers import register_exception_handlers
from app.core.exceptions import NotFoundException


class Payload(BaseModel):
    """请求体测试模型。"""

    name: str


def create_test_app() -> FastAPI:
    """创建用于异常处理测试的 FastAPI 应用实例。"""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/app-exception")
    def app_exception_route() -> None:
        raise NotFoundException("Resource not found")

    @app.get("/http-exception")
    def http_exception_route() -> None:
        raise HTTPException(status_code=403, detail="Forbidden")

    @app.post("/validation")
    def validation_route(payload: Payload) -> Payload:
        return payload

    @app.get("/unhandled")
    def unhandled_route() -> None:
        raise RuntimeError("secret internal error")

    return app


def test_app_exception_uses_unified_response() -> None:
    """验证自定义业务异常返回统一格式响应。"""
    client = TestClient(create_test_app())

    response = client.get("/app-exception")

    assert response.status_code == 404
    assert response.json() == {
        "code": "NOT_FOUND",
        "message": "Resource not found",
        "data": None,
    }


def test_http_exception_uses_unified_response() -> None:
    """验证 HTTPException 返回统一格式响应。"""
    client = TestClient(create_test_app())

    response = client.get("/http-exception")

    assert response.status_code == 403
    assert response.json() == {
        "code": "FORBIDDEN",
        "message": "Forbidden",
        "data": None,
    }


def test_validation_exception_uses_unified_response() -> None:
    """验证请求体校验失败返回详细验证错误信息。"""
    client = TestClient(create_test_app())

    response = client.post("/validation", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "Invalid request payload"
    assert isinstance(body["data"]["details"], list)
    assert "detail" not in body


def test_unhandled_exception_hides_internal_details() -> None:
    """验证未预期异常隐藏内部细节，不泄露敏感信息。"""
    client = TestClient(create_test_app(), raise_server_exceptions=False)

    response = client.get("/unhandled")

    assert response.status_code == 500
    assert response.json() == {
        "code": "INTERNAL_SERVER_ERROR",
        "message": "Internal server error",
        "data": None,
    }
    assert "secret internal error" not in response.text
    assert "Traceback" not in response.text
