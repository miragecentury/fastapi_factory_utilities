"""Package for books API."""

from .routes import api_v1_books_router, api_v2_books_router

__all__: list[str] = ["api_v1_books_router", "api_v2_books_router"]
