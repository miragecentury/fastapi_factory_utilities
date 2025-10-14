"""Abstracts for the plugins."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from fastapi_factory_utilities.core.protocols import ApplicationAbstractProtocol


class PluginAbstract(ABC):
    """Abstract class for the plugins."""

    def __init__(self) -> None:
        """Initialize the plugin."""
        self._application: ApplicationAbstractProtocol | None = None

    def set_application(self, application: "ApplicationAbstractProtocol") -> Self:
        """Set the application."""
        self._application = application
        return self

    def _add_to_state(self, key: str, value: Any) -> None:
        """Add to the state."""
        assert self._application is not None
        setattr(self._application.get_asgi_app().state, key, value)

    @abstractmethod
    def on_load(self) -> None:
        """On load."""
        raise NotImplementedError

    @abstractmethod
    async def on_startup(self) -> None:
        """On startup."""
        raise NotImplementedError

    @abstractmethod
    async def on_shutdown(self) -> None:
        """On shutdown."""
        raise NotImplementedError
