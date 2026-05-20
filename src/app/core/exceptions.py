from typing import Any

from app.core.error_codes import ErrorCode


class AppException(Exception):
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
    def __init__(self, message: str = "Bad request", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.BAD_REQUEST,
            message=message,
            status_code=400,
            data=data,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401,
            data=data,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=message,
            status_code=403,
            data=data,
        )


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=message,
            status_code=404,
            data=data,
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict", data: Any | None = None) -> None:
        super().__init__(
            code=ErrorCode.CONFLICT,
            message=message,
            status_code=409,
            data=data,
        )
