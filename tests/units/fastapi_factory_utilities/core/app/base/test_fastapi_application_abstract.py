"""Test FastAPIApplicationAbstract."""

# pyright: reportPrivateUsage=false

from typing import cast

import fastapi
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route

from fastapi_factory_utilities.core.app.base.fastapi_application_abstract import (
    FastAPIAbstract,
    FastAPIConfigAbstract,
)


class TestFastAPIApplicationAbstract:
    """Test FastAPIApplicationAbstract."""

    DUMMY_CONFIG = FastAPIConfigAbstract(
        title="Dummy",
        description="Dummy description",
        version="0.1.0",
    )

    def test_validate_fastapi_app_is_instanciate_correctly(self) -> None:
        """Test FastAPI application is instanciate."""
        api_router: fastapi.APIRouter = fastapi.APIRouter()
        api_router.add_api_route("/test", lambda: "Hello, World!", methods=["GET"])
        fastapi_app_abstract: FastAPIAbstract = FastAPIAbstract(config=self.DUMMY_CONFIG, api_router=api_router)

        # Assert FastAPI application is instanciate
        fastapi_app: fastapi.FastAPI = fastapi_app_abstract._fastapi_app  # pylint: disable=protected-access
        assert fastapi_app is not None
        assert isinstance(fastapi_app, fastapi.FastAPI)

        # Assert FastAPI application configuration
        assert fastapi_app.title == self.DUMMY_CONFIG.title
        assert fastapi_app.description == self.DUMMY_CONFIG.description
        assert fastapi_app.version == self.DUMMY_CONFIG.version

        # Assert FastAPI application router is included
        assert fastapi_app.router is not None
        assert len(fastapi_app.router.routes) >= 1
        test_route: Route | None = next(
            filter(
                lambda route: route.path == "/test",  # type: ignore
                cast(list[Route], fastapi_app.router.routes),
            ),
            None,
        )
        assert test_route is not None

        # Assert CORS middleware is defined
        assert fastapi_app.user_middleware is not None
        assert len(fastapi_app.user_middleware) == 1
        assert fastapi_app.user_middleware[0].__dict__["cls"] == CORSMiddleware

        # Assert CORS middleware configuration
        cors_middleware: Middleware = fastapi_app.user_middleware[0]
        assert cors_middleware.kwargs["allow_origins"] == ["*"]
        assert cors_middleware.kwargs["allow_credentials"] is True
        assert cors_middleware.kwargs["allow_methods"] == ["*"]
        assert cors_middleware.kwargs["allow_headers"] == ["*"]
