"""Provides enums for Kratos."""

from enum import StrEnum


class AuthenticatorAssuranceLevelEnum(StrEnum):
    """Enum for Authenticator Assurance Level (AAL)."""

    AAL1 = "aal1"
    AAL2 = "aal2"
    AAL3 = "aal3"
