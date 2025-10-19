"""API v1 sys health module.

Provide the Get health endpoint
"""

from http import HTTPStatus

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from fastapi_factory_utilities.core.services.status.enums import HealthStatusEnum
from fastapi_factory_utilities.core.services.status.services import (
    StatusService,
    depends_status_service,
)
from fastapi_factory_utilities.core.services.status.types import ComponentInstanceKey

api_v1_sys_health = APIRouter(prefix="/health")


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
def get_api_v1_sys_health(
    response: Response, status_service: StatusService = Depends(depends_status_service)
) -> HealthResponseModel:
    """Get the health of the system.

    Args:
        response (Response): The response object.
        status_service (StatusService): The status service.

    Returns:
        HealthResponse: The health status.
    """
    status: HealthStatusEnum = status_service.get_status()["health"]
    match status:
        case HealthStatusEnum.HEALTHY:
            response.status_code = HTTPStatus.OK.value
        case HealthStatusEnum.UNHEALTHY:
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    return HealthResponseModel(status=status)


class ComponentHealthResponseModel(BaseModel):
    """Component health response schema."""

    components: dict[ComponentInstanceKey, HealthStatusEnum]


@api_v1_sys_health.get(
    path="/components",
    tags=["sys"],
    response_model=ComponentHealthResponseModel,
    responses={
        HTTPStatus.OK.value: {
            "model": ComponentHealthResponseModel,
            "description": "Health status of all components.",
        },
    },
)
def get_api_v1_sys_components_health(
    status_service: StatusService = Depends(depends_status_service),
) -> ComponentHealthResponseModel:
    """Get the health of all components.

    Args:
        status_service (StatusService): The status service.

    Returns:
        list[ComponentHealthResponseModel]: The health status of all components.
    """
    components_dict: dict[ComponentInstanceKey, HealthStatusEnum] = {}

    for _, components in status_service.get_components_status_by_type().items():
        for key, status in components.items():
            components_dict[key] = status["health"]

    return ComponentHealthResponseModel(components=dict(components_dict))
