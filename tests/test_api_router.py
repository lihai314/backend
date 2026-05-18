from fastapi.routing import APIRoute

from app.api.router import api_router


def test_api_router_includes_health_route() -> None:
    paths = {route.path for route in api_router.routes if isinstance(route, APIRoute)}

    assert "/api/v1/health" in paths
