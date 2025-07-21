"""Package for books entities."""

from .entities import BookEntity
from .enums import BookType
from .types import BookName

__all__: list[str] = ["BookEntity", "BookName", "BookType"]
