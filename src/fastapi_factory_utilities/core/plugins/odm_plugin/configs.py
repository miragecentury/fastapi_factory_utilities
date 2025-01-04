"""Provides the configuration for the ODM plugin."""

from pydantic import BaseModel, ConfigDict

S_TO_MS = 1000


class ODMConfig(BaseModel):
    """Provides the configuration model for the ODM plugin."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    uri: str

    database: str = "test"

    connection_timeout_ms: int = 1 * S_TO_MS
