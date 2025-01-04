"""Repository for books."""

from fastapi_factory_utilities.core.plugins.odm_plugin.repositories import (
    AbstractRepository,
)
from fastapi_factory_utilities.example.entities.books import BookEntity
from fastapi_factory_utilities.example.models.books.document import BookDocument


class BookRepository(AbstractRepository[BookDocument, BookEntity]):
    """Repository for books."""
