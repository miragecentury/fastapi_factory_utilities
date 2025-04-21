"""Provides the Kratos Objects."""

import datetime
import uuid
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from .enums import AuthenticatorAssuranceLevelEnum


class KratosTraitsObject(BaseModel):
    """Traits for Kratos."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore")

    email: str
    username: str
    realm_id: uuid.UUID


class KratosIdentityObject(BaseModel):
    """Identity for Kratos."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore")

    id: uuid.UUID
    state: str
    traits: KratosTraitsObject


class KratosSessionObject(BaseModel):
    """Session object for Kratos."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore")

    id: uuid.UUID
    active: bool
    issued_at: datetime.datetime
    expires_at: datetime.datetime
    authenticated_at: datetime.datetime
    authenticator_assurance_level: AuthenticatorAssuranceLevelEnum
    identity: KratosIdentityObject
