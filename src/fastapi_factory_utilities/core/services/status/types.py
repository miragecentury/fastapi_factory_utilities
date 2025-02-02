"""Provides the status types for the service."""

import datetime
from typing import ClassVar, NewType, TypedDict, cast

from pydantic import BaseModel, ConfigDict

from .enums import ComponentTypeEnum, HealthStatusEnum, ReadinessStatusEnum

ComponentInstanceKey = NewType("ComponentInstanceKey", str)


class ComponentInstanceType:
    """Component instance type.

    Attributes:
        component_type (ComponentTypeEnum): The component type.
        identifier (str | None): The identifier.
        key (ComponentInstanceKey): The key based on the component type and identifier.
    """

    def _generate_key(self) -> ComponentInstanceKey:
        """Generate the key identifier for the component instance.

        It is based on the component type and identifier.

        Returns:
            str: The key.

        """
        key: str = (
            f"{self._component_type.value}:{self._identifier}" if self._identifier else self._component_type.value
        )
        return cast(ComponentInstanceKey, key)

    def __init__(self, component_type: ComponentTypeEnum, identifier: str | None = None) -> None:
        """Initialize the component instance type.

        Args:
            component_type (ComponentTypeEnum): The component type.
            identifier (str, optional): The identifier. Defaults to None.

        """
        self._component_type: ComponentTypeEnum = component_type
        self._identifier: str | None = identifier
        self._key: ComponentInstanceKey = self._generate_key()

    @property
    def component_type(self) -> ComponentTypeEnum:
        """Get the component type.

        Returns:
            ComponentTypeEnum: The component type.

        """
        return self._component_type

    @property
    def identifier(self) -> str | None:
        """Get the identifier.

        Returns:
            str | None: The identifier.

        """
        return self._identifier

    @property
    def key(self) -> ComponentInstanceKey:
        """Get the key.

        Returns:
            str: The key.

        """
        return self._key


class Status(TypedDict):
    """Status type.

    Attributes:
        health (HealthStatusEnum): The health status.
        readiness (ReadinessStatusEnum): The readiness status.
    """

    health: HealthStatusEnum
    readiness: ReadinessStatusEnum


class StatusUpdateEvent(BaseModel):
    """Status update event."""

    # Pydantic config
    model_config: ClassVar[ConfigDict] = {"frozen": True}

    # Health status
    health_status: HealthStatusEnum
    previous_health_status: HealthStatusEnum

    # Readiness status
    readiness_status: ReadinessStatusEnum
    previous_readiness_status: ReadinessStatusEnum

    # Timestamp
    triggered_at: datetime.datetime


class ComponentInstanceStatusUpdateEvent(BaseModel):
    """Component instance status update event."""

    # Pydantic config
    model_config: ClassVar[ConfigDict] = {
        "frozen": True,
        "arbitrary_types_allowed": True,  # Needed for the ComponentInstanceType
    }

    # Component instance
    component_instance: ComponentInstanceType

    # Health status
    health_status: HealthStatusEnum

    # Readiness status
    readiness_status: ReadinessStatusEnum

    # Timestamp
    triggered_at: datetime.datetime
