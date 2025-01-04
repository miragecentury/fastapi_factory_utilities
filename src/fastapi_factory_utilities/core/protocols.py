"""Protocols for the base application."""

from abc import abstractmethod
from typing import TYPE_CHECKING, ClassVar, Protocol, runtime_checkable

from beanie import Document
from fastapi import FastAPI

if TYPE_CHECKING:
    from fastapi_factory_utilities.core.app.base.config_abstract import (
        AppConfigAbstract,
    )


class BaseApplicationProtocol(Protocol):
    """Protocol for the base application."""

    PACKAGE_NAME: str

    ODM_DOCUMENT_MODELS: ClassVar[list[type[Document]]]

    @abstractmethod
    def get_config(self) -> "AppConfigAbstract":
        """Get the application configuration."""

    @abstractmethod
    def get_asgi_app(self) -> FastAPI:
        """Get the ASGI application."""


@runtime_checkable
class PluginProtocol(Protocol):
    """Defines the protocol for the plugin.

    Attributes:
        INJECTOR_MODULE (type[Module]): The module for the plugin.

    """

    @abstractmethod
    def pre_conditions_check(self, application: BaseApplicationProtocol) -> bool:
        """Check the pre-conditions for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            bool: True if the pre-conditions are met, False otherwise.
        """

    @abstractmethod
    def on_load(self, application: BaseApplicationProtocol) -> None:
        """The actions to perform on load for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            None
        """

    @abstractmethod
    async def on_startup(self, application: BaseApplicationProtocol) -> None:
        """The actions to perform on startup for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            None
        """

    @abstractmethod
    async def on_shutdown(self, application: BaseApplicationProtocol) -> None:
        """The actions to perform on shutdown for the plugin.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            None
        """
