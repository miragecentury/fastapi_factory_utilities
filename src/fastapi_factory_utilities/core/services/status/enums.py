"""Provides the status enums for the service."""

from enum import StrEnum


class HealthStatusEnum(StrEnum):
    """Health status enum."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class ReadinessStatusEnum(StrEnum):
    """Readiness status enum."""

    READY = "ready"
    NOT_READY = "not_ready"


class ComponentTypeEnum(StrEnum):
    """Component type enum."""

    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    STORAGE = "storage"
    MESSAGE_BROKER = "message_broker"
    SEARCH_ENGINE = "search_engine"
    TASK_QUEUE = "task_queue"
    OTHER = "other"
