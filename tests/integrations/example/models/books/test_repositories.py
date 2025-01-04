"""Provides unit tests for the BookRepository class."""

from typing import Any, cast
from uuid import uuid4

import beanie
import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

from fastapi_factory_utilities.example.entities.books import (
    BookEntity,
    BookName,
    BookType,
)
from fastapi_factory_utilities.example.models.books.document import BookDocument
from fastapi_factory_utilities.example.models.books.repository import BookRepository


class TestBookRepository:
    """Unit tests for the BookRepository class."""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_create(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test create method.

        Args:
            async_motor_database (AsyncIOMotorDatabase): The async motor database.
        """
        await beanie.init_beanie(database=async_motor_database, document_models=[BookDocument])  # pyright: ignore
        book_repository = BookRepository(database=async_motor_database)

        book_entity_created: BookEntity = await book_repository.insert(
            entity=BookEntity(
                id=uuid4(),
                title=BookName("The Hobbit"),
                book_type=BookType.FANTASY,
            )
        )

        assert book_entity_created.title == BookName("The Hobbit")
        assert book_entity_created.book_type == BookType.FANTASY

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_one_by_id(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test get_one_by_id method.

        Args:
            async_motor_database (AsyncIOMotorDatabase): The async motor database.
        """
        await beanie.init_beanie(database=async_motor_database, document_models=[BookDocument])  # pyright: ignore
        book_repository = BookRepository(database=async_motor_database)

        book_entity_created: BookEntity = await book_repository.insert(
            entity=BookEntity(
                id=uuid4(),
                title=BookName("The Hobbit"),
                book_type=BookType.FANTASY,
            )
        )

        book_entity_retrieved: BookEntity = cast(
            BookEntity, await book_repository.get_one_by_id(entity_id=book_entity_created.id)
        )

        assert book_entity_retrieved.title == BookName("The Hobbit")
        assert book_entity_retrieved.book_type == BookType.FANTASY

    @pytest.mark.asyncio(loop_scope="session")
    async def test_delete_one_by_id(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test delete_one_by_id method.

        Args:
            async_motor_database (AsyncIOMotorDatabase): The async motor database.
        """
        await beanie.init_beanie(database=async_motor_database, document_models=[BookDocument])  # pyright: ignore
        book_repository = BookRepository(database=async_motor_database)

        book_entity_created: BookEntity = await book_repository.insert(
            entity=BookEntity(
                id=uuid4(),
                title=BookName("The Hobbit"),
                book_type=BookType.FANTASY,
            )
        )

        await book_repository.delete_one_by_id(entity_id=book_entity_created.id)

        book_entity_retrieved: BookEntity = cast(
            BookEntity, await book_repository.get_one_by_id(entity_id=book_entity_created.id)
        )

        assert book_entity_retrieved is None
