"""Provides an abstract class for FastAPI application integration."""

from abc import ABC
from typing import Any

import starlette.types
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_factory_utilities.core.app.config import RootConfig


class FastAPIAbstract(ABC):
    """Application integration with FastAPI.

    TODO: Replace by a Factory pattern.
    """

    def __init__(
        self,
        config: RootConfig,
        api_router: APIRouter | None = None,
        lifespan: starlette.types.StatelessLifespan[starlette.types.ASGIApp] | None = None,
    ) -> None:
        """Instanciate the FastAPI application.

        Args:
            config (FastAPIConfigAbstract): The FastAPI configuration.
            api_router (APIRouter, optional): The API router to include.
                Defaults to None.
            lifespan (AsyncGenerator[None, None], optional): The lifespan

        Returns:
            None

        """
        self._fastapi_app: FastAPI = FastAPI(
            title=config.application.service_name,
            description=config.application.description,
            version=config.application.version,
            root_path=config.application.root_path,
            debug=config.development.debug,
            lifespan=lifespan,
        )

        # TODO: Add CORS middleware Configuration
        self._fastapi_app.add_middleware(
            middleware_class=CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        if api_router is not None:
            self._fastapi_app.include_router(router=api_router)

    def get_asgi_app(self) -> FastAPI:
        """Get the ASGI application."""
        return self._fastapi_app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        """Forward the call to the FastAPI app."""
        return await self._fastapi_app.__call__(scope=scope, receive=receive, send=send)
