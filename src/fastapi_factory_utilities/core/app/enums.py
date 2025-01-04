"""Provides enums for the app module."""

from enum import StrEnum


class EnvironmentEnum(StrEnum):
    """Represents the environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
