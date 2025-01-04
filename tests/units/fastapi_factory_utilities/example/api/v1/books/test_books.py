"""Tests for the books API."""

from http import HTTPStatus
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from fastapi_factory_utilities.core.app.base.plugins_manager_abstract import (
    PluginsActivationList,
)
from fastapi_factory_utilities.example.api.books.routes import get_book_service
from fastapi_factory_utilities.example.app.app import App
from fastapi_factory_utilities.example.services.books.services import BookService


class TestBookApi:
    """Tests for the books API."""

    def test_get_books(self) -> None:
        """Test get_books."""
        application: App = App.build(plugin_activation_list=PluginsActivationList(activate=[]))

        application.get_asgi_app().dependency_overrides[get_book_service] = lambda: MagicMock(
            spec=BookService, return_value=[]
        )

        with TestClient(application) as client:
            response = client.get("/api/v1/books")

            assert response.status_code == HTTPStatus.OK
            assert response.json()["books"] == []
