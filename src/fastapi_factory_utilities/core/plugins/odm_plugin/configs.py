"""Provides the configuration for the ODM plugin."""

from pydantic import BaseModel, ConfigDict


class ODMConfig(BaseModel):
    """Provides the configuration model for the ODM plugin."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    uri: str

    database: str = "test"

    connection_timeout_ms: int = 1000
