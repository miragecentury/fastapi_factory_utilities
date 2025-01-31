"""Provides services for books."""

from typing import ClassVar
from uuid import UUID

from fastapi import Request
from opentelemetry import metrics

from fastapi_factory_utilities.core.plugins.odm_plugin.depends import (
    depends_odm_database,
)
from fastapi_factory_utilities.core.plugins.opentelemetry_plugin.helpers import (
    trace_span,
)
from fastapi_factory_utilities.example.entities.books import (
    BookEntity,
    BookName,
    BookType,
)
from fastapi_factory_utilities.example.models.books.repository import BookRepository


class BookService:
    """Provides services for books."""

    book_store: ClassVar[dict[UUID, BookEntity]] = {}

    # Metrics Definitions
    METER_COUNTER_BOOK_GET_NAME: str = "book_get"
    METER_COUNTER_BOOK_ADD_NAME: str = "book_add"
    METER_COUNTER_BOOK_REMOVE_NAME: str = "book_remove"
    METER_COUNTER_BOOK_UPDATE_NAME: str = "book_update"
    # ====================

    meter: metrics.Meter = metrics.get_meter(__name__)

    METER_COUNTER_BOOK_GET: metrics.Counter = meter.create_counter(
        name=METER_COUNTER_BOOK_GET_NAME, description="The number of books retrieved."
    )
    METER_COUNTER_BOOK_ADD: metrics.Counter = meter.create_counter(
        name=METER_COUNTER_BOOK_ADD_NAME,
        description="The number of books added.",
    )
    METER_COUNTER_BOOK_REMOVE: metrics.Counter = meter.create_counter(
        name=METER_COUNTER_BOOK_REMOVE_NAME,
        description="The number of books removed.",
    )
    METER_COUNTER_BOOK_UPDATE: metrics.Counter = meter.create_counter(
        name=METER_COUNTER_BOOK_UPDATE_NAME,
        description="The number of books updated.",
    )

    def __init__(
        self,
        book_repository: BookRepository,
    ) -> None:
        """Initialize the service.

        Args:
            book_repository (injector.Inject[BookRepository]): The book repository.
            meter (metrics.Meter, optional): The meter. Defaults to None use for testing purpose.

        Raises:
            ValueError: If the book already exists.

        """
        self.book_repository: BookRepository = book_repository

        # Build the book store if it is empty
        if len(self.book_store) == 0:
            self.build_book_store()

    @classmethod
    def build_default_book_store(cls) -> list[BookEntity]:
        """Build the default book store."""
        return [
            BookEntity(title=BookName("Book 1"), book_type=BookType.FANTASY),
            BookEntity(title=BookName("Book 2"), book_type=BookType.MYSTERY),
            BookEntity(title=BookName("Book 3"), book_type=BookType.SCIENCE_FICTION),
        ]

    @classmethod
    def build_book_store(cls, books: list[BookEntity] | None = None) -> None:
        """Build the book store.

        Args:
            books (list[BookEntity], optional): The books to add. Defaults to None.
        """
        if books is None:
            books = cls.build_default_book_store()

        cls.book_store = {book.id: book for book in books}

    @trace_span(name="Add Book")
    def add_book(self, book: BookEntity) -> None:
        """Add a book.

        Args:
            book (BookEntity): The book to add

        Raises:
            ValueError: If the book already exists.
        """
        if book.id in self.book_store:
            raise ValueError(f"Book with id {book.id} already exists.")

        self.book_store[book.id] = book

        self.METER_COUNTER_BOOK_ADD.add(amount=1)

    def get_book(self, book_id: UUID) -> BookEntity:
        """Get a book.

        Args:
            book_id (UUID): The book id

        Returns:
            BookEntity: The book

        Raises:
            ValueError: If the book does not exist.
        """
        if book_id not in self.book_store:
            raise ValueError(f"Book with id {book_id} does not exist.")

        self.METER_COUNTER_BOOK_GET.add(amount=1, attributes={"book_count": 1})

        return self.book_store[book_id]

    def get_all_books(self) -> list[BookEntity]:
        """Get all books.

        Returns:
            list[BookEntity]: All books
        """
        self.METER_COUNTER_BOOK_GET.add(amount=1, attributes={"book_count": len(self.book_store)})
        return list(self.book_store.values())

    @trace_span(name="Remove Book")
    def remove_book(self, book_id: UUID) -> None:
        """Remove a book.

        Args:
            book_id (UUID): The book id

        Raises:
            ValueError: If the book does not exist.
        """
        if book_id not in self.book_store:
            raise ValueError(f"Book with id {book_id} does not exist.")

        del self.book_store[book_id]

        self.METER_COUNTER_BOOK_REMOVE.add(amount=1)

    @trace_span(name="Update Book")
    def update_book(self, book: BookEntity) -> None:
        """Update a book.

        Args:
            book (BookEntity): The book to update

        Raises:
            ValueError: If the book does not exist.
        """
        if book.id not in self.book_store:
            raise ValueError(f"Book with id {book.id} does not exist.")

        self.book_store[book.id] = book

        self.METER_COUNTER_BOOK_UPDATE.add(amount=1)


def depends_book_service(request: Request) -> BookService:
    """Provide Book Service."""
    return BookService(book_repository=BookRepository(database=depends_odm_database(request=request)))
