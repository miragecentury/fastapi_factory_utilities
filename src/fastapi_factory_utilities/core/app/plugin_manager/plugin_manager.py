"""Plugin manager.

This module provides the plugin manager for the application.

Objective:
    - Provide a way to manage plugins for the application.
    - The plugins are activated based on the configuration.
    - The plugins are checked for pre-conditions.
    - The plugins are loaded on application load.
    - The plugins are started on application startup.
    - The plugins are stopped on application shutdown.
"""

from importlib import import_module
from types import ModuleType
from typing import Self

from fastapi_factory_utilities.core.app.plugin_manager.plugin_state import PluginState
from fastapi_factory_utilities.core.plugins import PluginsEnum
from fastapi_factory_utilities.core.protocols import (
    BaseApplicationProtocol,
    PluginProtocol,
)

from .exceptions import (
    InvalidPluginError,
    PluginManagerError,
    PluginPreConditionNotMetError,
)


class PluginManager:
    """Plugin manager for the application."""

    DEFAULT_PLUGIN_PACKAGE: str = "fastapi_factory_utilities.core.plugins"

    @classmethod
    def _import_module(cls, name: str, package: str) -> ModuleType:
        """Import the module. This is a wrapper around the import_module function to be able to mock it in the tests.

        Args:
            name (str): The name of the module.
            package (str): The package of the module.

        Returns:
            ModuleType: The module.

        Raises:
            ImportError: If the module cannot be imported.
            ModuleNotFoundError: If the module is not found.
        """
        return import_module(name=f"{package}.{name}")

    @classmethod
    def _check_pre_conditions(
        cls, plugin_package: str, want_to_activate_plugins: list[PluginsEnum], application: BaseApplicationProtocol
    ) -> list[PluginProtocol]:
        """Check the pre-conditions for the plugins.

        Args:
            plugin_package (str): The package for the plugins.
            want_to_activate_plugins (list[PluginsEnum]): The plugins to activate.
            application (BaseApplicationProtocol): The application.

        Returns:
            list[PluginProtocol]: The activated plugins.

        Raises:
            InvalidPluginError: If the plugin is invalid.
            PluginPreConditionNotMetError: If the pre-conditions are not met.
        """
        plugins: list[PluginProtocol] = []

        for plugin_enum in want_to_activate_plugins:

            try:
                # Using a custom import function to be able to mock it in the tests.
                plugin_module: ModuleType = cls._import_module(name=plugin_enum.value, package=plugin_package)
            except (ImportError, ModuleNotFoundError) as import_error:
                # TODO: Later, if we introduce extra mecanism to manage dependencies,
                # we must handle a part of the error here. To be able to provide a better error message.
                # For now, we just raise the error.
                raise InvalidPluginError(
                    plugin_name=plugin_enum.value, message="Error importing the plugin "
                ) from import_error

            if not isinstance(plugin_module, PluginProtocol):
                raise InvalidPluginError(
                    plugin_name=plugin_enum.value, message="The plugin does not implement the PluginProtocol"
                )

            if not plugin_module.pre_conditions_check(application=application):
                raise PluginPreConditionNotMetError(
                    plugin_name=plugin_enum.value, message="The pre-conditions are not met"
                )

            plugins.append(plugin_module)

        return plugins

    def __init__(self, activated: list[PluginsEnum] | None = None, plugin_package: str | None = None) -> None:
        """Instanciate the plugin manager."""
        self._plugin_package: str = plugin_package or self.DEFAULT_PLUGIN_PACKAGE
        self._plugins_wanted_to_be_activated: list[PluginsEnum] = activated or []
        self._activated_plugins: list[PluginProtocol] = []
        self._states: dict[str, PluginState] = {}

    @property
    def states(self) -> dict[str, PluginState]:
        """Get the states."""
        return self._states

    def add_application_context(self, application: BaseApplicationProtocol) -> Self:
        """Add the application context to the plugins.

        Args:
            application (BaseApplicationProtocol): The application.

        Returns:
            Self: The plugin manager.
        """
        self._application: BaseApplicationProtocol = application

        return self

    def add_states(self, states: list[PluginState]) -> Self:
        """Add the states to the plugin manager.

        Args:
            states (list[PluginState]): The states.

        Returns:
            Self: The plugin manager.
        """
        for state in states:
            if state.key in self._states:
                raise PluginManagerError(f"The state with key {state.key} already exists.")
            self._states[state.key] = state

        return self

    def load(self) -> Self:
        """Load the plugins.

        Returns:
            Self: The plugin manager.

        Raises:
            InvalidPluginError: If the plugin is invalid.
            PluginPreConditionNotMetError: If the pre-conditions are not met.

        """
        # Check the pre-conditions for the plugins.
        self._activated_plugins = self._check_pre_conditions(
            plugin_package=self._plugin_package,
            want_to_activate_plugins=self._plugins_wanted_to_be_activated,
            application=self._application,
        )
        # Load from the previous check.
        for plugin in self._activated_plugins:
            self.add_states(states=plugin.on_load(application=self._application) or [])

        return self

    async def trigger_startup(self) -> Self:
        """Trigger the startup of the plugins."""
        for plugin in self._activated_plugins:
            self.add_states(states=await plugin.on_startup(application=self._application) or [])

        return self

    async def trigger_shutdown(self) -> Self:
        """Trigger the shutdown of the plugins."""
        for plugin in self._activated_plugins:
            await plugin.on_shutdown(application=self._application)

        return self
