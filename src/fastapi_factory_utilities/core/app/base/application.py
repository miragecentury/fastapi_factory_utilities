"""Provides the abstract class for the application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import ClassVar, Self, cast

import starlette.types
from beanie import Document
from fastapi import FastAPI

from fastapi_factory_utilities.core.api import api
from fastapi_factory_utilities.core.plugins import PluginsEnum
from fastapi_factory_utilities.core.utils.log import LogModeEnum, setup_log

from ..config import RootConfig, RootConfigBuilder
from ..plugin_manager import PluginManager
from .fastapi_application_abstract import FastAPIAbstract


class BaseApplication(FastAPIAbstract):
    """Application abstract class."""

    PACKAGE_NAME: str = ""

    CONFIG_CLASS: ClassVar[type[RootConfig]] = RootConfig

    ODM_DOCUMENT_MODELS: ClassVar[list[type[Document]]] = []

    def __init__(self, config: RootConfig, plugin_activation_list: list[PluginsEnum] | None = None) -> None:
        """Instantiate the application.

        Args:
            config (AppConfigAbstract): The application configuration.
            plugin_activation_list (PluginsActivationList | None, optional): The plugins activation list.

        Returns:
            None

        Raises:
            ValueError: If the package name is not set.
        """
        if self.PACKAGE_NAME == "":
            raise ValueError("The package name must be set in the concrete application class.")

        self._config: RootConfig = config
        FastAPIAbstract.__init__(
            self=cast(FastAPIAbstract, self),
            config=self._config,
            api_router=api,
            lifespan=cast(starlette.types.StatelessLifespan[starlette.types.ASGIApp], self.fastapi_lifespan),
        )
        self._plugin_manager: PluginManager = PluginManager(activated=plugin_activation_list)
        self._plugin_manager.add_application_context(application=self)
        self._plugin_manager.load()

    @classmethod
    def main(cls) -> None:
        """Main function.

        This must be the same for all applications.
        """
        from fastapi_factory_utilities.core.utils.uvicorn import (  # pylint: disable=import-outside-toplevel
            UvicornUtils,
        )

        setup_log(mode=LogModeEnum.CONSOLE)
        application: BaseApplication = cls.build()
        uvicorn_utils = UvicornUtils(app=application)

        try:
            uvicorn_utils.serve()
        except KeyboardInterrupt:
            pass

    @classmethod
    def build_config(cls) -> RootConfig:
        """Build the application configuration.

        Returns:
            AppConfigAbstract: The application configuration.
        """
        config_builder: RootConfigBuilder = RootConfigBuilder(
            package_name=cls.PACKAGE_NAME, config_class=cls.CONFIG_CLASS
        )
        return config_builder.build()

    @classmethod
    def build(cls, config: RootConfig | None = None, plugin_activation_list: list[PluginsEnum] | None = None) -> Self:
        """Build the application.

        Args:
            config (AppConfigAbstract | None, optional): The application configuration. Defaults to None.
            plugin_activation_list (list[PluginsEnum] | None, optional): The plugins activation list.
            Defaults to None.
        """
        if config is None:
            config = cls.build_config()

        return cls(config=config, plugin_activation_list=plugin_activation_list)

    @asynccontextmanager
    async def fastapi_lifespan(self, fastapi_application: FastAPI) -> AsyncGenerator[None, None]:
        """Provide the lifespan context manager for FastAPI.

        Args:
            fastapi_application (FastAPI): The FastAPI application.

        Returns:
            AsyncGenerator[None]: The lifespan context manager.
        """
        del fastapi_application
        await self._plugin_manager.trigger_startup()
        yield
        await self._plugin_manager.trigger_shutdown()

    def get_config(self) -> RootConfig:
        """Get the application configuration."""
        return self._config
