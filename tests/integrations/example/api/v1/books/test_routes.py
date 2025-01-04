"""Tests for the routes of the books API."""

import os
from http import HTTPStatus
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from structlog.stdlib import get_logger

from fastapi_factory_utilities.example.app.app import App

_logger = get_logger(__package__)


class TestBooksRoutes:
    """Tests for the routes of the books API."""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_books(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test get_books."""
        with patch.dict(
            os.environ,
            {
                "MONGO_URI": async_motor_database.client.delegate._init_kwargs[  # pylint: disable=protected-access
                    "host"
                ],
            },
        ):
            _logger.debug(f"MONGO_URI={os.getenv('MONGO_URI')}")

            with TestClient(App.build()) as client:
                response: Response = client.get("/api/v1/books")
                assert response.status_code == HTTPStatus.OK
