"""Provides the concrete application class."""

from typing import ClassVar

from beanie import Document

from fastapi_factory_utilities.core.app import BaseApplication
from fastapi_factory_utilities.core.app.base.plugins_manager_abstract import (
    PluginsActivationList,
)
from fastapi_factory_utilities.example.models.books.document import BookDocument

from .config import AppConfig


class App(BaseApplication):
    """Concrete application class."""

    PACKAGE_NAME: str = "fastapi_factory_utilities.example"

    CONFIG_CLASS = AppConfig

    ODM_DOCUMENT_MODELS: ClassVar[list[type[Document]]] = [BookDocument]

    def __init__(self, config: AppConfig, plugin_activation_list: PluginsActivationList | None = None) -> None:
        """Instantiate the application with the configuration and the API router.

        Args:
            config (AppConfig): The application configuration.
            plugin_activation_list (PluginsActivationList | None, optional): The plugins activation list.
        """
        super().__init__(config=config, plugin_activation_list=plugin_activation_list)

        # Prevent circular imports
        from ..api import api_router  # pylint: disable=import-outside-toplevel

        self.get_asgi_app().include_router(router=api_router)
