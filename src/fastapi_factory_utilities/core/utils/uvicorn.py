"""Provides utilities for the application."""

import uvicorn
import uvicorn.server

from fastapi_factory_utilities.core.protocols import ApplicationAbstractProtocol
from fastapi_factory_utilities.core.utils.log import clean_uvicorn_logger


class UvicornUtils:
    """Provides utilities for Uvicorn."""

    def __init__(self, app: ApplicationAbstractProtocol) -> None:
        """Instantiate the factory.

        Args:
            app (BaseApplication): The application.

        Returns:
            None
        """
        self._app: ApplicationAbstractProtocol = app

    def build_uvicorn_config(self) -> uvicorn.Config:
        """Build the Uvicorn configuration.

        Returns:
            uvicorn.Config: The Uvicorn configuration.
        """
        config = uvicorn.Config(
            app=self._app.get_asgi_app(),
            host=self._app.get_config().server.host,
            port=self._app.get_config().server.port,
            reload=self._app.get_config().development.reload,
            workers=self._app.get_config().server.workers,
        )
        clean_uvicorn_logger()
        return config

    def serve(self) -> None:
        """Serve the application."""
        config: uvicorn.Config = self.build_uvicorn_config()
        server: uvicorn.Server = uvicorn.Server(config=config)
        server.run()
