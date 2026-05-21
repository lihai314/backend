"""业务异常定义，构建分层异常体系以支持统一错误处理。"""

from typing import Any

from app.core.error_codes import ErrorCode


class AppException(Exception):
    """应用级基础异常，包含业务错误码、状态码和可选附加数据。"""

    def __init__(
        self,
        code: ErrorCode | str,
        message: str,
        status_code: int = 400,
        data: Any | None = None,
    ) -> None:
        self.code = str(code)
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(message)


class BadRequestException(AppException):
    """请求参数错误异常（400），用于参数验证或请求格式错误。"""

    def __init__(self, message: str = "Bad request", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.BAD_REQUEST,
            message=message,
            status_code=400,
            data=data,
        )


class UnauthorizedException(AppException):
    """未认证异常（401），用于未提供或提供无效的身份凭证。"""

    def __init__(self, message: str = "Unauthorized", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401,
            data=data,
        )


class ForbiddenException(AppException):
    """权限不足异常（403），用于已认证但无访问权限的场景。"""

    def __init__(self, message: str = "Forbidden", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            status_code=403,
            data=data,
        )


class NotFoundException(AppException):
    """资源不存在异常（404）。"""

    def __init__(self, message: str = "Resource not found", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=404,
            data=data,
        )


class ConflictException(AppException):
    """资源冲突异常（409），用于唯一约束冲突等场景。"""

    def __init__(self, message: str = "Conflict", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.CONFLICT,
            message=message,
            status_code=409,
            data=data,
        )
