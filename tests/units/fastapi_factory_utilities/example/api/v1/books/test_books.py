"""Tests for the books API."""

from http import HTTPStatus
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from fastapi_factory_utilities.example.app import App, AppBuilder
from fastapi_factory_utilities.example.services.books.services import (
    BookService,
    depends_book_service,
)


class TestBookApi:
    """Tests for the books API."""

    def test_get_books(self) -> None:
        """Test get_books."""
        application: App = AppBuilder(plugins_activation_list=[]).build()

        application.get_asgi_app().dependency_overrides[depends_book_service] = lambda: MagicMock(
            spec=BookService, return_value=[]
        )

        with TestClient(application) as client:
            response = client.get("/api/v1/books")

            assert response.status_code == HTTPStatus.OK
            assert response.json()["books"] == []
