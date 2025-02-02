"""API v1 sys readiness module.

Provide the Get readiness endpoint
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from fastapi_factory_utilities.core.services.status.enums import ReadinessStatusEnum
from fastapi_factory_utilities.core.services.status.services import (
    StatusService,
    depends_status_service,
)

api_v1_sys_readiness = APIRouter(prefix="/readiness")


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
def get_api_v1_sys_readiness(
    response: Response, status_service: StatusService = Depends(depends_status_service)
) -> ReadinessResponseModel:
    """Get the readiness of the system.

    Args:
        response (Response): The response object.
        status_service (StatusService): The status service

    Returns:
        ReadinessResponse: The readiness status.
    """
    status: ReadinessStatusEnum = status_service.get_status()["readiness"]

    match status:
        case ReadinessStatusEnum.READY:
            response.status_code = HTTPStatus.OK.value
        case ReadinessStatusEnum.NOT_READY:
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    return ReadinessResponseModel(status=status)
