"""Readiness calculator strategies."""

from typing import Protocol

from .enums import ReadinessStatusEnum
from .types import ComponentInstanceKey, Status


class ReadinessCalculatorStrategy(Protocol):
    """Readiness calculator strategy."""

    def __init__(self, components_status: dict[ComponentInstanceKey, Status]) -> None:
        """Initialize the readiness calculator.

        Args:
            components_status (dict[str, Status]): The components status.
        """
        raise NotImplementedError

    def calculate(self) -> ReadinessStatusEnum:
        """Calculate the readiness status."""
        raise NotImplementedError


class ReadinessSimpleCalculatorStrategy:
    """Readiness calculator."""

    def __init__(self, components_status: dict[ComponentInstanceKey, Status]) -> None:
        """Initialize the readiness calculator.

        Args:
            components_status (dict[str, Status]): The components status.
        """
        self._components_status: dict[ComponentInstanceKey, Status] = components_status

    def calculate(self) -> ReadinessStatusEnum:
        """Calculate the readiness status."""
        for status in self._components_status.values():
            if status["readiness"] != ReadinessStatusEnum.READY:
                return ReadinessStatusEnum.NOT_READY
        return ReadinessStatusEnum.READY
