from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.common import ApiResponse

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    status: str


@router.get("/health", response_model=ApiResponse[HealthStatus])
def health() -> ApiResponse[HealthStatus]:
    return ApiResponse(
        code="OK",
        message="ok",
        data=HealthStatus(status="healthy"),
    )
