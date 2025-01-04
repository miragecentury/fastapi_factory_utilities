"""Package for plugins."""

from enum import StrEnum, auto


class PluginsEnum(StrEnum):
    """Enumeration for the plugins."""

    OPENTELEMETRY_PLUGIN = auto()
    ODM_PLUGIN = auto()


__all__: list[str] = [
    "PluginsEnum",
]
