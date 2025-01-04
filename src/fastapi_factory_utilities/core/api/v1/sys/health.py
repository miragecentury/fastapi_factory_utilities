"""API v1 sys health module.

Provide the Get health endpoint
"""

from enum import StrEnum
from http import HTTPStatus

from fastapi import APIRouter, Response
from pydantic import BaseModel

api_v1_sys_health = APIRouter(prefix="/health")


class HealthStatusEnum(StrEnum):
    """Health status enum."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class HealthResponseModel(BaseModel):
    """Health response schema."""

    status: HealthStatusEnum


@api_v1_sys_health.get(
    path="",
    tags=["sys"],
    response_model=HealthResponseModel,
    responses={
        HTTPStatus.OK.value: {
            "model": HealthResponseModel,
            "description": "Health status.",
        },
        HTTPStatus.INTERNAL_SERVER_ERROR.value: {
            "model": HealthResponseModel,
            "description": "Internal server error.",
        },
    },
)
def get_api_v1_sys_health(response: Response) -> HealthResponseModel:
    """Get the health of the system.

    Args:
        response (Response): The response object.

    Returns:
        HealthResponse: The health status.
    """
    response.status_code = HTTPStatus.OK
    return HealthResponseModel(status=HealthStatusEnum.HEALTHY)
