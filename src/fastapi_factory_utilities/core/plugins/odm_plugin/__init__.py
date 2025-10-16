"""ODM Plugin Module."""

from .depends import depends_odm_client, depends_odm_database
from .documents import BaseDocument
from .exceptions import (
    ODMPluginBaseException,
    ODMPluginConfigError,
    OperationError,
    UnableToCreateEntityDueToDuplicateKeyError,
)
from .helpers import PersistedEntity
from .plugins import ODMPlugin
from .repositories import AbstractRepository

__all__: list[str] = [
    "AbstractRepository",
    "BaseDocument",
    "ODMPlugin",
    "ODMPluginBaseException",
    "ODMPluginConfigError",
    "OperationError",
    "PersistedEntity",
    "UnableToCreateEntityDueToDuplicateKeyError",
    "depends_odm_client",
    "depends_odm_database",
]
