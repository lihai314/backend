"""API 路由聚合测试，验证子路由正确挂载。"""

from fastapi.routing import APIRoute

from app.api.router import api_router


def test_api_router_includes_expected_routes() -> None:
    """验证核心路由被正确挂载到 /api/v1 前缀下。"""
    paths = {route.path for route in api_router.routes if isinstance(route, APIRoute)}

    assert "/api/v1/health" in paths
    assert "/api/v1/auth/register" in paths
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/logout" in paths
    assert "/api/v1/users/me" in paths
    assert "/api/v1/users/me/actions/change-password" in paths
