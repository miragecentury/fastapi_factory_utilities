"""Provides utilities for the application."""

import uvicorn
import uvicorn.server

from fastapi_factory_utilities.core.protocols import BaseApplicationProtocol
from fastapi_factory_utilities.core.utils.log import clean_uvicorn_logger


class UvicornUtils:
    """Provides utilities for Uvicorn."""

    def __init__(self, app: BaseApplicationProtocol) -> None:
        """Instantiate the factory.

        Args:
            app (BaseApplication): The application.
            config (AppConfigAbstract): The application configuration.

        Returns:
            None
        """
        self._app: BaseApplicationProtocol = app

    def build_uvicorn_config(self) -> uvicorn.Config:
        """Build the Uvicorn configuration.

        Returns:
            uvicorn.Config: The Uvicorn configuration.
        """
        config = uvicorn.Config(
            app=self._app.get_asgi_app(),
            host=self._app.get_config().host,
            port=self._app.get_config().port,
            reload=self._app.get_config().reload,
            workers=self._app.get_config().workers,
        )
        clean_uvicorn_logger()
        return config

    def serve(self) -> None:
        """Serve the application."""
        config: uvicorn.Config = self.build_uvicorn_config()
        server: uvicorn.Server = uvicorn.Server(config=config)
        server.run()
