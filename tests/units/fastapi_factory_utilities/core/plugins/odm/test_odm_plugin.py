"""Provide the unit tests for the ODM plugin."""

from importlib import import_module
from types import ModuleType

from fastapi_factory_utilities.core.protocols import PluginProtocol


class TestODMPlugin:
    """Test the ODM plugin."""

    def test_is_valid_plugin(self) -> None:
        """Test the valid plugin."""
        odm_plugin: ModuleType = import_module("fastapi_factory_utilities.core.plugins.odm_plugin")
        assert isinstance(odm_plugin, PluginProtocol)
