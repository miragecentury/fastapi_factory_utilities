"""Provides the monitored abstract class for monitoring the status of the application.

```python
# Example of using the MonitoredAbstract


class MyMonitored(MonitoredAbstract):
    def __init__(self, status_service: StatusService) -> None:
        super().__init__(
            component_instance=ComponentInstanceType(
                component_type=ComponentTypeEnum.APPLICATION,
                component_name="MyMonitored",
            ),
            status_service=status_service,
        )

    def my_method(self) -> None:
        self.update_monitoring_status(
            Status(
                status_type=StatusTypeEnum.INFO,
                status_message="My method is running.",
            )
        )
```

"""

from abc import ABC

from reactivex import Subject

from fastapi_factory_utilities.core.services.status import (
    ComponentInstanceType,
    ComponentTypeEnum,
    Status,
    StatusService,
)


class MonitoredAbstract(ABC):
    """Monitored abstract class."""

    def __init__(self, component_instance: ComponentInstanceType, status_service: StatusService) -> None:
        """Initialize the monitored.

        Args:
            component_instance (ComponentInstanceType): The component instance.
            status_service (StatusService): The status service.

        """
        self._monit_component_instance: ComponentInstanceType = component_instance
        self._monit_status_service_subject: Subject[Status] = status_service.register_component_instance(
            component_instance=component_instance
        )

    def update_monitoring_status(self, status: Status) -> None:
        """Update the monitoring status.

        Args:
            status (Status): The status.

        """
        self._monit_status_service_subject.on_next(status)


__all__: list[str] = [
    "MonitoredAbstract",
    "ComponentInstanceType",
    "ComponentTypeEnum",
    "Status",
    "StatusService",
]
