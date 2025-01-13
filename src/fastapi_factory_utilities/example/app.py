"""Provides the concrete application class."""

from typing import ClassVar

from beanie import Document

from fastapi_factory_utilities.core.app.application import ApplicationAbstract
from fastapi_factory_utilities.core.app.builder import ApplicationGenericBuilder
from fastapi_factory_utilities.core.app.config import RootConfig
from fastapi_factory_utilities.core.plugins import PluginsEnum
from fastapi_factory_utilities.example.models.books.document import BookDocument


class AppRootConfig(RootConfig):
    """Application configuration class."""

    pass


class App(ApplicationAbstract):
    """Concrete application class."""

    CONFIG_CLASS: ClassVar[type[RootConfig]] = AppRootConfig

    PACKAGE_NAME: ClassVar[str] = "fastapi_factory_utilities.example"

    ODM_DOCUMENT_MODELS: ClassVar[list[type[Document]]] = [BookDocument]

    DEFAULT_PLUGINS_ACTIVATED: ClassVar[list[PluginsEnum]] = [PluginsEnum.OPENTELEMETRY_PLUGIN, PluginsEnum.ODM_PLUGIN]

    def configure(self) -> None:
        """Configure the application."""
        # Prevent circular import
        from .api import api_router  # pylint: disable=import-outside-toplevel

        self.get_asgi_app().include_router(router=api_router)

    async def on_startup(self) -> None:
        """Actions to perform on application startup."""
        pass

    async def on_shutdown(self) -> None:
        """Actions to perform on application shutdown."""
        pass


class AppBuilder(ApplicationGenericBuilder[App]):
    """Application builder for the App application."""

    pass
