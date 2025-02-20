"""Provides the Books API."""

from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends

from fastapi_factory_utilities.example.entities.books import BookEntity
from fastapi_factory_utilities.example.services.books import (
    BookService,
    depends_book_service,
)

from .responses import BookListReponse, BookResponseModel

api_v1_books_router: APIRouter = APIRouter(prefix="/books")
api_v2_books_router: APIRouter = APIRouter(prefix="/books")


@api_v1_books_router.get(path="", response_model=BookListReponse)
def get_books(
    books_service: BookService = Depends(depends_book_service),
) -> BookListReponse:
    """Get all books.

    Args:
        books_service (BookService): Book service.

    Returns:
        BookListReponse: List of books
    """
    books: list[BookEntity] = books_service.get_all_books()

    return BookListReponse(
        books=cast(
            list[BookResponseModel],
            map(lambda book: BookResponseModel(**book.model_dump()), books),
        ),
        size=len(books),
    )


@api_v1_books_router.get(path="/{book_id}", response_model=BookResponseModel)
def get_book(
    book_id: UUID,
    books_service: BookService = Depends(depends_book_service),
) -> BookResponseModel:
    """Get a book.

    Args:
        book_id (str): Book id
        books_service (BookService): Book service

    Returns:
        BookResponseModel: Book
    """
    book: BookEntity = books_service.get_book(book_id)

    return BookResponseModel(**book.model_dump())
