"""Provide tests for AbstractRepository class."""

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


class RepositoryForTest(AbstractRepository[DocumentForTest, EntityForTest]):
    """Test repository class."""

    pass


class TestAbstractRepository:
    """Test AbstractRepository class."""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_insert(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test insert method."""
        await init_beanie(database=async_motor_database, document_models=[DocumentForTest])
        repository: RepositoryForTest = RepositoryForTest(database=async_motor_database)
        entity_id: UUID = uuid4()
        entity: EntityForTest = EntityForTest(id=entity_id, my_field="my_field")
        entity_created = await repository.insert(entity=entity)

        assert entity_created.id == entity_id
        assert entity_created.my_field == "my_field"

    @pytest.mark.asyncio(loop_scope="session")
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

    @pytest.mark.asyncio(loop_scope="session")
    async def test_delete_one(self, async_motor_database: AsyncIOMotorDatabase[Any]) -> None:
        """Test delete_one method."""
        await init_beanie(database=async_motor_database, document_models=[DocumentForTest])
        repository: RepositoryForTest = RepositoryForTest(database=async_motor_database)
        entity_id: UUID = uuid4()
        entity: EntityForTest = EntityForTest(id=entity_id, my_field="my_field")
        entity_created: EntityForTest = await repository.insert(entity=entity)
        await repository.delete_one_by_id(entity_id=entity_created.id)
