"""Oriented Data Model (ODM) plugin package."""

from logging import INFO, Logger, getLogger
from typing import Any

from beanie import init_beanie  # pyright: ignore[reportUnknownVariableType]
from motor.motor_asyncio import AsyncIOMotorClient
from reactivex import Subject
from structlog.stdlib import BoundLogger, get_logger

from fastapi_factory_utilities.core.plugins import PluginState
from fastapi_factory_utilities.core.protocols import ApplicationAbstractProtocol
from fastapi_factory_utilities.core.services.status.enums import (
    ComponentTypeEnum,
    HealthStatusEnum,
    ReadinessStatusEnum,
)
from fastapi_factory_utilities.core.services.status.services import StatusService
from fastapi_factory_utilities.core.services.status.types import (
    ComponentInstanceType,
    Status,
)

from .builder import ODMBuilder
from .depends import depends_odm_client, depends_odm_database
from .documents import BaseDocument
from .exceptions import OperationError, UnableToCreateEntityDueToDuplicateKeyError
from .repositories import AbstractRepository

_logger: BoundLogger = get_logger()


def pre_conditions_check(application: ApplicationAbstractProtocol) -> bool:
    """Check the pre-conditions for the OpenTelemetry plugin.

    Args:
        application (BaseApplicationProtocol): The application.

    Returns:
        bool: True if the pre-conditions are met, False otherwise.
    """
    del application
    return True


def on_load(
    application: ApplicationAbstractProtocol,
) -> list["PluginState"] | None:
    """Actions to perform on load for the OpenTelemetry plugin.

    Args:
        application (BaseApplicationProtocol): The application.
    """
    del application
    # Configure the pymongo logger to INFO level
    pymongo_logger: Logger = getLogger("pymongo")
    pymongo_logger.setLevel(INFO)
    _logger.debug("ODM plugin loaded.")


async def on_startup(
    application: ApplicationAbstractProtocol,
) -> list["PluginState"] | None:
    """Actions to perform on startup for the ODM plugin.

    Args:
        application (BaseApplicationProtocol): The application.
        odm_config (ODMConfig): The ODM configuration.

    Returns:
        None
    """
    states: list[PluginState] = []

    status_service: StatusService = application.get_status_service()
    component_instance: ComponentInstanceType = ComponentInstanceType(
        component_type=ComponentTypeEnum.DATABASE, identifier="MongoDB"
    )
    monitoring_subject: Subject[Status] = status_service.register_component_instance(
        component_instance=component_instance
    )

    try:
        odm_factory: ODMBuilder = ODMBuilder(application=application).build_all()
        await odm_factory.wait_ping()
    except Exception as exception:  # pylint: disable=broad-except
        _logger.error(f"ODM plugin failed to start. {exception}")
        # TODO: Report the error to the status_service
        # this will report the application as unhealthy
        monitoring_subject.on_next(
            value=Status(health=HealthStatusEnum.UNHEALTHY, readiness=ReadinessStatusEnum.NOT_READY)
        )
        return states

    if odm_factory.odm_database is None or odm_factory.odm_client is None:
        _logger.error(
            f"ODM plugin failed to start. Database: {odm_factory.odm_database} - " f"Client: {odm_factory.odm_client}"
        )
        # TODO: Report the error to the status_service
        # this will report the application as unhealthy
        monitoring_subject.on_next(
            value=Status(health=HealthStatusEnum.UNHEALTHY, readiness=ReadinessStatusEnum.NOT_READY)
        )
        return states

    # Add the ODM client and database to the application state
    states.append(
        PluginState(key="odm_client", value=odm_factory.odm_client),
    )
    states.append(
        PluginState(
            key="odm_database",
            value=odm_factory.odm_database,
        ),
    )

    # TODO: Find a better way to initialize beanie with the document models of the concrete application
    # through an hook in the application, a dynamis import ?
    try:
        await init_beanie(
            database=odm_factory.odm_database,
            document_models=application.ODM_DOCUMENT_MODELS,
        )
    except Exception as exception:  # pylint: disable=broad-except
        _logger.error(f"ODM plugin failed to start. {exception}")
        # TODO: Report the error to the status_service
        # this will report the application as unhealthy
        monitoring_subject.on_next(
            value=Status(health=HealthStatusEnum.UNHEALTHY, readiness=ReadinessStatusEnum.NOT_READY)
        )
        return states

    _logger.info(
        f"ODM plugin started. Database: {odm_factory.odm_database.name} - "
        f"Client: {odm_factory.odm_client.address} - "
        f"Document models: {application.ODM_DOCUMENT_MODELS}"
    )

    monitoring_subject.on_next(value=Status(health=HealthStatusEnum.HEALTHY, readiness=ReadinessStatusEnum.READY))

    return states


async def on_shutdown(application: ApplicationAbstractProtocol) -> None:
    """Actions to perform on shutdown for the ODM plugin.

    Args:
        application (BaseApplicationProtocol): The application.

    Returns:
        None
    """
    # Skip if the ODM plugin was not started correctly
    if not hasattr(application.get_asgi_app().state, "odm_client"):
        return

    client: AsyncIOMotorClient[Any] = application.get_asgi_app().state.odm_client
    client.close()
    _logger.debug("ODM plugin shutdown.")


__all__: list[str] = [
    "BaseDocument",
    "AbstractRepository",
    "OperationError",
    "UnableToCreateEntityDueToDuplicateKeyError",
    "depends_odm_client",
    "depends_odm_database",
]
