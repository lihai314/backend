"""核心辅助函数测试，补充异常映射、默认消息和业务异常分支覆盖。"""

from app.core.error_codes import ErrorCode
from app.core.exception_handlers import (
    default_message_for_status_code,
    map_status_code_to_error_code,
)
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
)


def test_map_status_code_to_error_code_covers_common_statuses() -> None:
    """验证常见 HTTP 状态码能映射为统一业务错误码。"""
    assert map_status_code_to_error_code(400) == ErrorCode.BAD_REQUEST
    assert map_status_code_to_error_code(401) == ErrorCode.UNAUTHORIZED
    assert map_status_code_to_error_code(403) == ErrorCode.FORBIDDEN
    assert map_status_code_to_error_code(404) == ErrorCode.NOT_FOUND
    assert map_status_code_to_error_code(409) == ErrorCode.CONFLICT
    assert map_status_code_to_error_code(422) == ErrorCode.VALIDATION_ERROR
    assert map_status_code_to_error_code(500) == ErrorCode.INTERNAL_SERVER_ERROR


def test_default_message_for_status_code_covers_common_statuses() -> None:
    """验证常见 HTTP 状态码默认错误消息。"""
    assert default_message_for_status_code(400) == "Bad request"
    assert default_message_for_status_code(401) == "Unauthorized"
    assert default_message_for_status_code(403) == "Forbidden"
    assert default_message_for_status_code(404) == "Not found"
    assert default_message_for_status_code(409) == "Conflict"
    assert default_message_for_status_code(422) == "Invalid request payload"
    assert default_message_for_status_code(500) == "Internal server error"
    assert default_message_for_status_code(418) == "Request failed"


def test_builtin_app_exceptions_define_status_code_and_error_code() -> None:
    """验证内置业务异常携带正确状态码、错误码和附加数据。"""
    bad_request = BadRequestException(data={"field": "name"})
    unauthorized = UnauthorizedException()
    forbidden = ForbiddenException()
    conflict = ConflictException()

    assert bad_request.status_code == 400
    assert bad_request.code == ErrorCode.BAD_REQUEST
    assert bad_request.data == {"field": "name"}

    assert unauthorized.status_code == 401
    assert unauthorized.code == ErrorCode.UNAUTHORIZED

    assert forbidden.status_code == 403
    assert forbidden.code == ErrorCode.FORBIDDEN

    assert conflict.status_code == 409
    assert conflict.code == ErrorCode.CONFLICT
