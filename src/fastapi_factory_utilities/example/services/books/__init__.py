"""Provide Books Service."""

from .services import BookService, depends_book_service

__all__: list[str] = ["BookService", "depends_book_service"]
