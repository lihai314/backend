"""错误码枚举，定义全局统一业务错误码。"""

from enum import StrEnum


class ErrorCode(StrEnum):
    """统一业务错误码枚举，与 HTTP 状态码对应但不直接耦合。"""

    OK = "OK"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
