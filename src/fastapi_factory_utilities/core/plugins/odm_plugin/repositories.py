"""Provides the abstract classes for the repositories."""

import datetime
from abc import ABC
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any, Generic, TypeVar, get_args
from uuid import UUID
from venv import create

from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.results import DeleteResult

from .documents import BaseDocument
from .exceptions import OperationError, UnableToCreateEntityDueToDuplicateKeyError

DocumentGenericType = TypeVar("DocumentGenericType", bound=BaseDocument)  # pylint: disable=invalid-name
EntityGenericType = TypeVar("EntityGenericType", bound=BaseModel)  # pylint: disable=invalid-name


def managed_session() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to manage the session.

    It will introspect the function arguments and check if the session is passed as a keyword argument.
    If it is not, it will create a new session and pass it to the function.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if "session" in kwargs:
                return await func(*args, **kwargs)

            async with args[0].get_session() as session:
                return await func(*args, **kwargs, session=session)

        return wrapper

    return decorator


class AbstractRepository(ABC, Generic[DocumentGenericType, EntityGenericType]):
    """Abstract class for the repository."""

    def __init__(self, database: AsyncIOMotorDatabase[Any]) -> None:
        """Initialize the repository."""
        super().__init__()
        self._database: AsyncIOMotorDatabase[Any] = database
        # Retrieve the generic concrete types
        generic_args: tuple[Any, ...] = get_args(self.__orig_bases__[0])  # type: ignore
        self._document_type: type[DocumentGenericType] = generic_args[0]
        self._entity_type: type[EntityGenericType] = generic_args[1]

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncIOMotorClientSession, None]:
        """Yield a new session."""
        try:
            async with await self._database.client.start_session() as session:
                yield session
        except PyMongoError as error:
            raise OperationError(f"Failed to create session: {error}") from error

    @managed_session()
    async def insert(
        self, entity: EntityGenericType, session: AsyncIOMotorClientSession | None = None
    ) -> EntityGenericType:
        """Insert the entity into the database.

        Args:
            entity (EntityGenericType): The entity to insert.
            session (AsyncIOMotorClientSession | None): The session to use. Defaults to None. (managed by decorator)

        Returns:
            EntityGenericType: The entity created.

        Raises:
            ValueError: If the entity cannot be created from the document.
            UnableToCreateEntityDueToDuplicateKeyError: If the entity cannot be created due to a duplicate key error.
            OperationError: If the operation fails.
        """
        insert_time: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        try:
            entity_dump: dict[str, Any] = entity.model_dump()
            entity_dump["created_at"] = insert_time
            entity_dump["updated_at"] = insert_time
            document: DocumentGenericType = self._document_type(**entity_dump)

        except ValueError as error:
            raise ValueError(f"Failed to create document from entity: {error}") from error

        try:
            document_created: DocumentGenericType = await document.save(session=session)
        except DuplicateKeyError as error:
            raise UnableToCreateEntityDueToDuplicateKeyError(f"Failed to insert document: {error}") from error
        except PyMongoError as error:
            raise OperationError(f"Failed to insert document: {error}") from error

        try:
            entity_created: EntityGenericType = self._entity_type(**document_created.model_dump())
        except ValueError as error:
            raise ValueError(f"Failed to create entity from document: {error}") from error

        return entity_created

    @managed_session()
    async def update(
        self, entity: EntityGenericType, session: AsyncIOMotorClientSession | None = None
    ) -> EntityGenericType:
        """Update the entity in the database.

        Args:
            entity (EntityGenericType): The entity to update.
            session (AsyncIOMotorClientSession | None): The session to use. Defaults to None. (managed by decorator)

        Returns:
            EntityGenericType: The updated entity.

        Raises:
            ValueError: If the entity cannot be created from the document.
            OperationError: If the operation fails.
        """
        update_time: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        try:
            entity_dump: dict[str, Any] = entity.model_dump()
            entity_dump["updated_at"] = update_time
            document: DocumentGenericType = self._document_type(**entity_dump)

        except ValueError as error:
            raise ValueError(f"Failed to create document from entity: {error}") from error

        try:
            document_updated: DocumentGenericType = await document.save(session=session)
        except PyMongoError as error:
            raise OperationError(f"Failed to update document: {error}") from error

        try:
            entity_updated: EntityGenericType = self._entity_type(**document_updated.model_dump())
        except ValueError as error:
            raise ValueError(f"Failed to create entity from document: {error}") from error

        return entity_updated

    @managed_session()
    async def get_one_by_id(
        self,
        entity_id: UUID,
        session: AsyncIOMotorClientSession | None = None,
    ) -> EntityGenericType | None:
        """Get the entity by its ID.

        Args:
            entity_id (UUID): The ID of the entity.
            session (AsyncIOMotorClientSession | None): The session to use. Defaults to None. (managed by decorator)

        Returns:
            EntityGenericType | None: The entity or None if not found.

        Raises:
            OperationError: If the operation fails.

        """
        try:
            document: DocumentGenericType | None = await self._document_type.get(document_id=entity_id, session=session)
        except PyMongoError as error:
            raise OperationError(f"Failed to get document: {error}") from error

        # If no document is found, return None
        if document is None:
            return None

        # Convert the document to an entity
        try:
            entity: EntityGenericType = self._entity_type(**document.model_dump())
        except ValueError as error:
            raise ValueError(f"Failed to create entity from document: {error}") from error

        return entity

    @managed_session()
    async def delete_one_by_id(
        self, entity_id: UUID, raise_if_not_found: bool = False, session: AsyncIOMotorClientSession | None = None
    ) -> None:
        """Delete a document by its ID.

        Args:
            entity_id (UUID): The ID of the entity.
            raise_if_not_found (bool, optional): Raise an exception if the document is not found. Defaults to False.
            session (AsyncIOMotorClientSession | None, optional): The session to use.
            Defaults to None. (managed by decorator)

        Raises:
            ValueError: If the document is not found and raise_if_not_found is True.
            OperationError: If the operation fails.

        """
        try:
            document_to_delete: DocumentGenericType | None = await self._document_type.get(
                document_id=entity_id, session=session
            )
        except PyMongoError as error:
            raise OperationError(f"Failed to get document to delete: {error}") from error

        if document_to_delete is None:
            if raise_if_not_found:
                raise ValueError(f"Failed to find document with ID {entity_id}")
            return

        try:
            delete_result: DeleteResult | None = await document_to_delete.delete()
        except PyMongoError as error:
            raise OperationError(f"Failed to delete document: {error}") from error

        if delete_result is not None and delete_result.deleted_count == 1 and delete_result.acknowledged:
            return

        raise OperationError("Failed to delete document.")
