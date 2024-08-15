"""
Package that contains the abstract classes
for the application and application configuration.
"""

from .base import (
    AppConfigAbstract,
    ApplicationConfigFactoryException,
    ApplicationFactoryException,
    BaseApplication,
    BaseApplicationException,
    GenericBaseApplicationModule,
)
from .enums import EnvironmentEnum

__all__: list[str] = [
    "BaseApplication",
    "AppConfigAbstract",
    "GenericBaseApplicationModule",
    "EnvironmentEnum",
    "ApplicationConfigFactoryException",
    "ApplicationFactoryException",
    "BaseApplicationException",
]