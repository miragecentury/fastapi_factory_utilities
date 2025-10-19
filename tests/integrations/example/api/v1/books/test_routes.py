"""Tests for the routes of the books API."""

import os
from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from structlog.stdlib import get_logger
from testcontainers.mongodb import MongoDbContainer

from fastapi_factory_utilities.example.app import AppBuilder

_logger = get_logger(__package__)


class TestBooksRoutes:
    """Tests for the routes of the books API."""

    @pytest.mark.asyncio()
    async def test_get_books(self, mongodb_server_as_container: MongoDbContainer) -> None:
        """Test get_books."""
        # Use the container's connection URL directly
        mongo_uri: str = mongodb_server_as_container.get_connection_url()

        with patch.dict(os.environ, {"MONGO_URI": mongo_uri}):
            _logger.debug(f"MONGO_URI={os.getenv('MONGO_URI')}")  # pylint: disable=inconsistent-quotes

            with TestClient(app=AppBuilder().build()) as client:
                response: Response = client.get("/api/v1/books")
                assert response.status_code == HTTPStatus.OK
