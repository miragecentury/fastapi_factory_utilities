"""Provide the ApplicationGenericBuilder class."""

from typing import Any, Generic, Self, TypeVar, get_args

from fastapi_factory_utilities.core.app.config import GenericConfigBuilder, RootConfig
from fastapi_factory_utilities.core.app.fastapi_builder import FastAPIBuilder
from fastapi_factory_utilities.core.app.plugin_manager.plugin_manager import (
    PluginManager,
)
from fastapi_factory_utilities.core.plugins import PluginsEnum
from fastapi_factory_utilities.core.utils.log import LogModeEnum, setup_log
from fastapi_factory_utilities.core.utils.uvicorn import UvicornUtils

from .application import ApplicationAbstract

T = TypeVar("T", bound=ApplicationAbstract)


class ApplicationGenericBuilder(Generic[T]):
    """Application generic builder."""

    def __init__(self, plugins_activation_list: list[PluginsEnum] | None = None) -> None:
        """Instanciate the ApplicationGenericBuilder."""
        self._uvicorn_utils: UvicornUtils | None = None
        self._root_config: RootConfig | None = None
        self._plugin_manager: PluginManager | None = None
        self._fastapi_builder: FastAPIBuilder | None = None
        generic_args: tuple[Any, ...] = get_args(self.__orig_bases__[0])  # type: ignore
        self._application_class: type[T] = generic_args[0]
        self._plugins_activation_list: list[PluginsEnum]
        if plugins_activation_list is None:
            self._plugins_activation_list = self._application_class.DEFAULT_PLUGINS_ACTIVATED
        else:
            self._plugins_activation_list = plugins_activation_list

    def add_plugin_to_activate(self, plugin: PluginsEnum) -> Self:
        """Add a plugin to activate.

        Args:
            plugin (PluginsEnum): The plugin to activate.

        Returns:
            Self: The builder.
        """
        self._plugins_activation_list.append(plugin)
        return self

    def add_config(self, config: RootConfig) -> Self:
        """Add the configuration to the builder.

        Args:
            config (RootConfig): The configuration.

        Returns:
            Self: The builder.
        """
        self._root_config = config
        return self

    def add_plugin_manager(self, plugin_manager: PluginManager) -> Self:
        """Add the plugin manager to the builder.

        Args:
            plugin_manager (PluginManager): The plugin manager.

        Returns:
            Self: The builder.
        """
        self._plugin_manager = plugin_manager
        return self

    def add_fastapi_builder(self, fastapi_builder: FastAPIBuilder) -> Self:
        """Add the FastAPI builder to the builder.

        Args:
            fastapi_builder (FastAPIBuilder): The FastAPI builder.

        Returns:
            Self: The builder.
        """
        self._fastapi_builder = fastapi_builder
        return self

    def _build_from_package_root_config(self) -> RootConfig:
        """Build the configuration from the package."""
        return GenericConfigBuilder[self._application_class.CONFIG_CLASS](
            package_name=self._application_class.PACKAGE_NAME,
            config_class=self._application_class.CONFIG_CLASS,
        ).build()

    def build(self, **kwargs: Any) -> T:
        """Build the application.

        Args:
            **kwargs: The keyword arguments to pass to the application.

        Returns:
            T: The application.
        """
        # Plugin manager
        if self._plugin_manager is None:
            self._plugin_manager = PluginManager()
        for plugin in self._plugins_activation_list:
            self._plugin_manager.activate(plugin=plugin)
        # RootConfig
        self._root_config = self._root_config or self._build_from_package_root_config()
        # FastAPIBuilder
        self._fastapi_builder = self._fastapi_builder or FastAPIBuilder(root_config=self._root_config)

        application: T = self._application_class(
            root_config=self._root_config,
            plugin_manager=self._plugin_manager,
            fastapi_builder=self._fastapi_builder,
            **kwargs,
        )
        application.setup()
        return application

    def build_as_uvicorn_utils(self) -> UvicornUtils:
        """Build the application and provide UvicornUtils."""
        self._uvicorn_utils = UvicornUtils(app=self.build())
        return self._uvicorn_utils

    def build_and_serve(self) -> None:
        """Build the application and serve it with Uvicorn."""
        uvicorn_utils: UvicornUtils = self._uvicorn_utils or self.build_as_uvicorn_utils()

        setup_log(mode=LogModeEnum.CONSOLE, logging_config=self._root_config.logging)

        try:
            uvicorn_utils.serve()
        except KeyboardInterrupt:
            pass
