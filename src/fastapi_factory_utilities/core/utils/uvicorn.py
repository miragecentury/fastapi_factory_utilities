"""Provides utilities for the application."""

import os
from typing import Any

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
        self._ssl_keyfile: str | os.PathLike[str] | None = None
        self._ssl_certfile: str | os.PathLike[str] | None = None
        self._ssl_keyfile_password: str | None = None

    def add_ssl_certificates(
        self,
        ssl_keyfile: str | os.PathLike[str] | None = None,
        ssl_certfile: str | os.PathLike[str] | None = None,
        ssl_keyfile_password: str | None = None,
    ) -> None:
        """Add SSL certificates to the application.

        Args:
            ssl_keyfile (str | os.PathLike[str] | None): The SSL key file.
            ssl_certfile (str | os.PathLike[str] | None): The SSL certificate file.
            ssl_keyfile_password (str | None): The SSL key file password.

        Returns:
            None
        """
        self._ssl_keyfile = ssl_keyfile
        self._ssl_certfile = ssl_certfile
        self._ssl_keyfile_password = ssl_keyfile_password

    def build_uvicorn_config(self) -> uvicorn.Config:
        """Build the Uvicorn configuration.

        Returns:
            uvicorn.Config: The Uvicorn configuration.
        """
        kwargs: dict[str, Any] = {}

        if self._ssl_keyfile:
            kwargs["ssl_keyfile"] = self._ssl_keyfile
        if self._ssl_certfile:
            kwargs["ssl_certfile"] = self._ssl_certfile
        if self._ssl_keyfile_password:
            kwargs["ssl_keyfile_password"] = self._ssl_keyfile_password

        config = uvicorn.Config(
            app=self._app.get_asgi_app(),
            host=self._app.get_config().server.host,
            port=self._app.get_config().server.port,
            reload=self._app.get_config().development.reload,
            workers=self._app.get_config().server.workers,
            **kwargs,
        )
        clean_uvicorn_logger()
        return config

    def serve(self) -> None:
        """Serve the application."""
        config: uvicorn.Config = self.build_uvicorn_config()
        server: uvicorn.Server = uvicorn.Server(config=config)
        server.run()
