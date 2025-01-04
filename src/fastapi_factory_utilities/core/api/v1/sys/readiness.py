"""API v1 sys readiness module.

Provide the Get readiness endpoint
"""

from enum import StrEnum
from http import HTTPStatus

from fastapi import APIRouter, Response
from pydantic import BaseModel

api_v1_sys_readiness = APIRouter(prefix="/readiness")


class ReadinessStatusEnum(StrEnum):
    """Readiness status enum."""

    READY = "ready"
    NOT_READY = "not_ready"


class ReadinessResponseModel(BaseModel):
    """Readiness response schema."""

    status: ReadinessStatusEnum


@api_v1_sys_readiness.get(
    path="",
    tags=["sys"],
    response_model=ReadinessResponseModel,
    responses={
        HTTPStatus.OK.value: {
            "model": ReadinessResponseModel,
            "description": "Readiness status.",
        },
        HTTPStatus.INTERNAL_SERVER_ERROR.value: {
            "model": ReadinessResponseModel,
            "description": "Internal server error.",
        },
    },
)
def get_api_v1_sys_readiness(response: Response) -> ReadinessResponseModel:
    """Get the readiness of the system.

    Args:
        response (Response): The response object.

    Returns:
        ReadinessResponse: The readiness status.
    """
    response.status_code = HTTPStatus.OK
    return ReadinessResponseModel(status=ReadinessStatusEnum.READY)
