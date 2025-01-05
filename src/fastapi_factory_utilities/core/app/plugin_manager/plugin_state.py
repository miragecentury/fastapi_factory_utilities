"""Provide PluginState class."""

from typing import Any


class PluginState:
    """PluginState represent the state a plugin which to be share to the application and other plugins."""

    def __init__(self, key: str, value: Any) -> None:
        """Initialize the PluginState."""
        self._key: str = key
        self._value = value

    @property
    def key(self) -> str:
        """Get the key."""
        return self._key

    @property
    def value(self) -> Any:
        """Get the value."""
        return self._value
