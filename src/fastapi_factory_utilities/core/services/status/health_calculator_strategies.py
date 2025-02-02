"""Health calculator strategies."""

from typing import Protocol, runtime_checkable

from .enums import HealthStatusEnum
from .types import ComponentInstanceKey, Status


@runtime_checkable
class HealthCalculatorStrategy(Protocol):
    """Health calculator strategy."""

    def __init__(self, components_status: dict[ComponentInstanceKey, Status]) -> None:
        """Initialize the health calculator.

        Args:
            components_status (dict[str, Status]): The components status.
        """
        raise NotImplementedError

    def calculate(self) -> HealthStatusEnum:
        """Calculate the health status."""
        raise NotImplementedError


class HealthSimpleCalculatorStrategy:
    """Health calculator.

    This class calculates the health status based on the components status.
    It's a simple implementation that returns unhealthy if at least one component is unhealthy for now.
    We want to enhance this class to support more complex health calculation in the future.
    ( )
    """

    def __init__(self, components_status: dict[ComponentInstanceKey, Status]) -> None:
        """Initialize the health calculator.

        Args:
            components_status (dict[str, Status]): The components status.
        """
        self._components_status: dict[ComponentInstanceKey, Status] = components_status

    def calculate(self) -> HealthStatusEnum:
        """Calculate the health status."""
        for status in self._components_status.values():
            if status["health"] != HealthStatusEnum.HEALTHY:
                return HealthStatusEnum.UNHEALTHY
        return HealthStatusEnum.HEALTHY
