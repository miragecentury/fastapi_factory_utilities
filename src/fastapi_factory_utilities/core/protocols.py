"""Protocols for the base application."""

from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

from beanie import Document
from fastapi import FastAPI

from fastapi_factory_utilities.core.plugins import PluginsEnum
from fastapi_factory_utilities.core.services.status.services import StatusService

if TYPE_CHECKING:
    from fastapi_factory_utilities.core.app.config import RootConfig
    from fastapi_factory_utilities.core.plugins import PluginState


class ApplicationAbstractProtocol(Protocol):
    """Protocol for the base application."""

    PACKAGE_NAME: ClassVar[str]

    ODM_DOCUMENT_MODELS: ClassVar[list[type[Document]]]

    DEFAULT_PLUGINS_ACTIVATED: ClassVar[list[PluginsEnum]]

    @abstractmethod
    def get_config(self) -> "RootConfig":
        """Get the application configuration."""

    @abstractmethod
    def get_asgi_app(self) -> FastAPI:
        """Get the ASGI application."""

    @abstractmethod
    def get_status_service(self) -> StatusService:
        """Get the status service."""


@runtime_checkable
class PluginProtocol(Protocol):
    """Defines the protocol for the plugins."""

    @abstractmethod
    def pre_conditions_check(self, application: ApplicationAbstractProtocol) -> bool:
        """Check the pre-conditions for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            bool: True if the pre-conditions are met, False otherwise.
        """

    @abstractmethod
    def on_load(self, application: ApplicationAbstractProtocol) -> list["PluginState"] | None:
        """The actions to perform on load for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            None
        """

    @abstractmethod
    async def on_startup(self, application: ApplicationAbstractProtocol) -> list["PluginState"] | None:
        """The actions to perform on startup for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            None
        """

    @abstractmethod
    async def on_shutdown(self, application: ApplicationAbstractProtocol) -> None:
        """The actions to perform on shutdown for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            None
        """
