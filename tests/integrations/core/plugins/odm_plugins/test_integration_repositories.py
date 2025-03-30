"""Provide tests for AbstractRepository class."""

import datetime
from typing import Any
from uuid import UUID, uuid4

import pytest
from beanie import init_beanie  # pyright: ignore[reportUnknownVariableType]
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from fastapi_factory_utilities.core.plugins.odm_plugin.documents import BaseDocument
from fastapi_factory_utilities.core.plugins.odm_plugin.repositories import (
    AbstractRepository,
)


class DocumentForTest(BaseDocument):
    """Test document class."""

    my_field: str = Field(description="My field.")


class EntityForTest(BaseModel):
    """Test entity class."""

    id: UUID
    my_field: str

    revision_id: UUID | None = Field(default=None)
    created_at: datetime.datetime | None = Field(default=None)
    updated_at: datetime.datetime | None = Field(default=None)


class RepositoryForTest(AbstractRepository[DocumentForTest, EntityForTest]):
    """Test repository class."""

    pass


class TestAbstractRepository:
    """Test AbstractRepository class."""

    @pytest.mark.asyncio()
    async def test_insert(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test insert method."""
        await init_beanie(database=async_motor_database, document_models=[DocumentForTest])
        repository: RepositoryForTest = RepositoryForTest(database=async_motor_database)
        entity_id: UUID = uuid4()
        entity: EntityForTest = EntityForTest(id=entity_id, my_field="my_field")
        entity_created = await repository.insert(entity=entity)

        assert entity_created.id == entity_id
        assert entity_created.my_field == "my_field"

        assert isinstance(entity_created.created_at, datetime.datetime)
        assert isinstance(entity_created.updated_at, datetime.datetime)
        assert entity_created.created_at == entity_created.updated_at

    @pytest.mark.asyncio()
    async def test_find_one(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test find_one method."""
        await init_beanie(database=async_motor_database, document_models=[DocumentForTest])
        repository: RepositoryForTest = RepositoryForTest(database=async_motor_database)
        entity_id: UUID = uuid4()
        entity: EntityForTest = EntityForTest(id=entity_id, my_field="my_field")
        entity_created: EntityForTest = await repository.insert(entity=entity)
        entity_found: EntityForTest = await repository.get_one_by_id(entity_id=entity_created.id)

        assert entity_found.id == entity_id
        assert entity_found.my_field == "my_field"

        assert isinstance(entity_found.created_at, datetime.datetime)
        assert isinstance(entity_found.updated_at, datetime.datetime)
        assert entity_found.created_at == entity_created.created_at

    @pytest.mark.asyncio()
    async def test_delete_one(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test delete_one method."""
        await init_beanie(database=async_motor_database, document_models=[DocumentForTest])
        repository: RepositoryForTest = RepositoryForTest(database=async_motor_database)
        entity_id: UUID = uuid4()
        entity: EntityForTest = EntityForTest(id=entity_id, my_field="my_field")
        entity_created: EntityForTest = await repository.insert(entity=entity)
        await repository.delete_one_by_id(entity_id=entity_created.id)

    @pytest.mark.asyncio()
    async def test_update_one(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test update_one method."""
        await init_beanie(database=async_motor_database, document_models=[DocumentForTest])
        repository: RepositoryForTest = RepositoryForTest(database=async_motor_database)
        entity_id: UUID = uuid4()
        entity: EntityForTest = EntityForTest(id=entity_id, my_field="my_field")
        entity_created: EntityForTest = await repository.insert(entity=entity)

        entity_created.my_field = "my_field_updated"
        entity_updated: EntityForTest = await repository.update(entity=entity_created)

        assert entity_updated.id == entity_id
        assert entity_updated.my_field == "my_field_updated"
        assert entity_updated.updated_at is not None
        assert entity_updated.created_at is not None
        assert entity_created.updated_at is not None
        assert entity_created.created_at is not None
        assert isinstance(entity_updated.created_at, datetime.datetime)
        assert isinstance(entity_updated.updated_at, datetime.datetime)
        assert entity_updated.created_at == entity_created.created_at
        assert entity_updated.updated_at > entity_created.updated_at
