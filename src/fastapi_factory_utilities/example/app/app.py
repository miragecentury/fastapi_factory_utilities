"""Provides the concrete application class."""

from typing import ClassVar

from beanie import Document

from fastapi_factory_utilities.core.app import BaseApplication
from fastapi_factory_utilities.core.app.config import RootConfig
from fastapi_factory_utilities.core.plugins import PluginsEnum
from fastapi_factory_utilities.example.models.books.document import BookDocument


class AppConfig(RootConfig):
    """Application configuration class."""

    pass


class App(BaseApplication):
    """Concrete application class."""

    PACKAGE_NAME: str = "fastapi_factory_utilities.example"

    CONFIG_CLASS: ClassVar[type[RootConfig]] = AppConfig

    ODM_DOCUMENT_MODELS: ClassVar[list[type[Document]]] = [BookDocument]

    DEFAULT_PLUGINS_ACTIVATED: ClassVar[list[PluginsEnum]] = [PluginsEnum.OPENTELEMETRY_PLUGIN, PluginsEnum.ODM_PLUGIN]

    def __init__(self, config: RootConfig, plugin_activation_list: list[PluginsEnum] | None = None) -> None:
        """Instantiate the application with the configuration and the API router.

        Args:
            config (AppConfig): The application configuration.
            plugin_activation_list (PluginsActivationList | None, optional): The plugins activation list.
        """
        if plugin_activation_list is None:
            plugin_activation_list = self.DEFAULT_PLUGINS_ACTIVATED
        super().__init__(config=config, plugin_activation_list=plugin_activation_list)

        # Prevent circular imports
        from ..api import api_router  # pylint: disable=import-outside-toplevel

        self.get_asgi_app().include_router(router=api_router)
        self.get_asgi_app().include_router(router=api_router)
