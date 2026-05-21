"""API 路由聚合测试，验证子路由正确挂载。"""

from fastapi.routing import APIRoute

from app.api.router import api_router


def test_api_router_includes_health_route() -> None:
    """验证健康检查路由被正确挂载在 /api/v1/health。"""
    paths = {route.path for route in api_router.routes if isinstance(route, APIRoute)}

    assert "/api/v1/health" in paths
