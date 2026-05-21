"""全局异常处理器，将各类异常统一转换为标准 JSON 响应格式。"""

import logging
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.types import ExceptionHandler

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def error_response(
    *,
    status_code: int,
    code: ErrorCode | str,
    message: str,
    data: Any | None = None,
) -> JSONResponse:
    """构建统一格式的错误 JSON 响应。"""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": str(code),
            "message": message,
            "data": data,
        },
    )


def map_status_code_to_error_code(status_code: int) -> ErrorCode:
    """将 HTTP 状态码映射为对应的业务错误码。"""
    if status_code == 401:
        return ErrorCode.UNAUTHORIZED
    if status_code == 403:
        return ErrorCode.FORBIDDEN
    if status_code == 404:
        return ErrorCode.NOT_FOUND
    if status_code == 409:
        return ErrorCode.CONFLICT
    if status_code == 422:
        return ErrorCode.VALIDATION_ERROR
    if status_code >= 500:
        return ErrorCode.INTERNAL_SERVER_ERROR
    return ErrorCode.BAD_REQUEST


def default_message_for_status_code(status_code: int) -> str:
    """根据 HTTP 状态码返回默认错误消息。"""
    if status_code == 400:
        return "Bad request"
    if status_code == 401:
        return "Unauthorized"
    if status_code == 403:
        return "Forbidden"
    if status_code == 404:
        return "Not found"
    if status_code == 409:
        return "Conflict"
    if status_code == 422:
        return "Invalid request payload"
    if status_code >= 500:
        return "Internal server error"
    return "Request failed"


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """处理自定义 AppException 业务异常。"""
    return error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        data=exc.data,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理 Starlette/FastAPI 原生 HTTPException。"""
    code = map_status_code_to_error_code(exc.status_code)
    message = str(exc.detail) if exc.detail else default_message_for_status_code(exc.status_code)

    return error_response(
        status_code=exc.status_code,
        code=code,
        message=message,
        data=None,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """处理请求体校验失败异常（422），返回详细验证错误信息。"""
    return error_response(
        status_code=422,
        code=ErrorCode.VALIDATION_ERROR,
        message="Invalid request payload",
        data={"details": exc.errors()},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底异常处理器，捕获所有未预期的异常并记录错误日志。"""
    logger.exception("Unhandled exception occurred", exc_info=exc)

    return error_response(
        status_code=500,
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="Internal server error",
        data=None,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """向 FastAPI 应用注册所有自定义异常处理器。"""
    app.add_exception_handler(AppException, cast(ExceptionHandler, app_exception_handler))
    app.add_exception_handler(HTTPException, cast(ExceptionHandler, http_exception_handler))
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(Exception, unhandled_exception_handler)
