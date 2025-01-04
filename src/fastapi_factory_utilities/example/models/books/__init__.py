"""Package for the book model and repository."""

from .document import BookDocument
from .repository import BookRepository

__all__: list[str] = ["BookRepository", "BookDocument"]
