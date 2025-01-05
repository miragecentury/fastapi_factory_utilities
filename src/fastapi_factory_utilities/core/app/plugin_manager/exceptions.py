"""Provide the exceptions for the plugin manager."""

from fastapi_factory_utilities.core.exceptions import FastAPIFactoryUtilitiesError


class PluginManagerError(FastAPIFactoryUtilitiesError):
    """Generic plugin manager error."""


class InvalidPluginError(PluginManagerError):
    """The plugin is invalid."""

    def __init__(self, plugin_name: str, message: str) -> None:
        """Instantiate the exception.

        Args:
            plugin_name (str): The plugin name.
            message (str): The message
        """
        super().__init__(message=f"Invalid plugin: {plugin_name}, {message}")


class PluginPreConditionNotMetError(PluginManagerError):
    """The plugin pre-condition is not met."""

    def __init__(self, plugin_name: str, message: str) -> None:
        """Instantiate the exception.

        Args:
            plugin_name (str): The plugin name.
            message (str): The message
        """
        super().__init__(message=f"Plugin pre-condition not met: {plugin_name}, {message}")
