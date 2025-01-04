"""Provides the Book entity."""

from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .enums import BookType
from .types import BookName


class BookEntity(BaseModel):
    """Book entity."""

    id: UUID = Field(title="Unique identifier of the book", default_factory=uuid4)
    title: BookName = Field(title="Title of the book")
    book_type: BookType = Field(title="Type of book")
