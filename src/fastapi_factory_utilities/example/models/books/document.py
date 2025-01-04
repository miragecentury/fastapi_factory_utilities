"""Model for Book."""

from typing import Annotated

from beanie import Indexed  # pyright: ignore[reportUnknownVariableType]

from fastapi_factory_utilities.core.plugins.odm_plugin.documents import BaseDocument
from fastapi_factory_utilities.example.entities.books import BookName, BookType


class BookDocument(BaseDocument):
    """BookModel."""

    title: Annotated[BookName, Indexed(unique=True)]
    book_type: Annotated[BookType, Indexed()]

    class Settings(BaseDocument.Settings):
        """Meta class for BookModel."""

        collection: str = "books"
