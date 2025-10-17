"""Tests for the routes of the books API."""

import os
import asyncio
from http import HTTPStatus
from typing import Any
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

        # Add a small delay to ensure MongoDB is fully ready
        await asyncio.sleep(2)

        with patch.dict(os.environ, {"MONGO_URI": mongo_uri}):
            _logger.debug(f"MONGO_URI={os.getenv('MONGO_URI')}")  # pylint: disable=inconsistent-quotes

            with TestClient(app=AppBuilder().build()) as client:
                response: Response = client.get("/api/v1/books")
                assert response.status_code == HTTPStatus.OK
