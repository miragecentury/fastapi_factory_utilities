"""Tests for the health calculator strategies."""

import pytest

from fastapi_factory_utilities.core.services.status import HealthStatusEnum, Status
from fastapi_factory_utilities.core.services.status.health_calculator_strategies import (
    HealthCalculatorStrategy,
    HealthSimpleCalculatorStrategy,
)
from fastapi_factory_utilities.core.services.status.types import ComponentInstanceKey


class TestHealthSimpleCalculatorStrategy:
    """Tests for the HealthSimpleCalculatorStrategy."""

    def test_implement_protocol(self) -> None:
        """It should implement the HealthCalculatorStrategy protocol."""
        assert isinstance(HealthSimpleCalculatorStrategy, HealthCalculatorStrategy)

    @pytest.mark.parametrize(
        argnames="components_status, expected",
        argvalues=[
            pytest.param(
                [HealthStatusEnum.HEALTHY, HealthStatusEnum.HEALTHY],  # components_status
                HealthStatusEnum.HEALTHY,  # expected
                id="all healthy",
            ),
            pytest.param(
                [HealthStatusEnum.HEALTHY, HealthStatusEnum.UNHEALTHY],  # components_status
                HealthStatusEnum.UNHEALTHY,  # expected
                id="one unhealthy",
            ),
            pytest.param(
                [HealthStatusEnum.UNHEALTHY, HealthStatusEnum.HEALTHY],  # components_status
                HealthStatusEnum.UNHEALTHY,  # expected
                id="one unhealthy alternative",
            ),
            pytest.param(
                [HealthStatusEnum.UNHEALTHY, HealthStatusEnum.UNHEALTHY],  # components_status
                HealthStatusEnum.UNHEALTHY,  # expected
                id="all unhealthy",
            ),
        ],
    )
    def test_calculate_healthy(self, components_status: list[HealthStatusEnum], expected: HealthStatusEnum) -> None:
        """It should return healthy if all components are healthy."""
        components_status_dict: dict[ComponentInstanceKey, Status] = {
            ComponentInstanceKey(f"component_{index}"): Status(health=status, readiness=None)  # type: ignore
            for index, status in enumerate(components_status)
        }
        strategy = HealthSimpleCalculatorStrategy(components_status=components_status_dict)
        assert strategy.calculate() == expected
