"""Provides the objects for the Hydra service."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class HydraTokenIntrospectObject(BaseModel):
    """Represents the object returned by the Hydra token introspection."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore")

    active: bool
    aud: list[str]
    client_id: str
    exp: int
    ext: dict[str, str] | None = None
    iat: int
    iss: str
    nbf: int
    obfuscated_subject: str | None = None
    scope: str
    sub: str
    token_type: str
    token_use: str
    username: str | None = None
