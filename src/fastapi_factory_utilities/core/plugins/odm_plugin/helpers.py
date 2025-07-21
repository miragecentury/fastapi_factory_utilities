"""Helper functions for ODM plugins."""

import datetime
import uuid

from pydantic import BaseModel, Field


class PersistedEntity(BaseModel):
    """Base class for persisted entities."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    revision_id: uuid.UUID | None = Field(default=None)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
