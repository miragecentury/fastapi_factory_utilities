"""Plugin manager tests."""

from enum import StrEnum
from importlib import import_module
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from fastapi_factory_utilities.core.app.plugin_manager.exceptions import (
    InvalidPluginError,
)
from fastapi_factory_utilities.core.app.plugin_manager.plugin_manager import (
    PluginManager,
)
from fastapi_factory_utilities.core.plugins import PluginsEnum, PluginState
from fastapi_factory_utilities.core.protocols import (
    ApplicationAbstractProtocol,
    PluginProtocol,
)


class TestPluginManger:
    """Test the plugin manager."""

    class PluginsEnumForTest(StrEnum):
        """Test plugins enum."""

        VALID_PLUGIN = "valid_plugin"
        INVALID_PLUGIN = "invalid_plugin"

    def test_check_precondition_for_a_valid_plugin(self) -> None:
        """Test the valid plugin."""
        # Arrange
        plugin_manager = PluginManager()
        application = MagicMock(ApplicationAbstractProtocol)
        with patch(
            "fastapi_factory_utilities.core.app.plugin_manager.plugin_manager.PluginManager._import_module"
        ) as mock_import_module:
            mock_import_module.return_value = import_module("fastapi_factory_utilities.core.plugins.example")
            # Act
            plugins: list[PluginProtocol] = plugin_manager._check_pre_conditions(  # pylint: disable=protected-access # pyright: ignore[reportPrivateUsage]
                plugin_package="",
                want_to_activate_plugins=cast(list[PluginsEnum], [self.PluginsEnumForTest.VALID_PLUGIN]),
                application=application,
            )
        # Assert
        assert len(plugins) == 1

    def test_check_precondition_for_an_invalid_plugin(self) -> None:
        """Test the invalid plugin."""
        # Arrange
        plugin_manager = PluginManager()
        application = MagicMock(ApplicationAbstractProtocol)
        with patch(
            "fastapi_factory_utilities.core.app.plugin_manager.plugin_manager.PluginManager._import_module"
        ) as mock_import_module:
            mock_import_module.return_value = object()
            # Assert
            with pytest.raises(InvalidPluginError):
                # Act
                plugin_manager._check_pre_conditions(  # pylint: disable=protected-access # pyright: ignore[reportPrivateUsage]
                    plugin_package="",
                    want_to_activate_plugins=cast(list[PluginsEnum], [self.PluginsEnumForTest.INVALID_PLUGIN]),
                    application=application,
                )

    @pytest.mark.parametrize(
        "raise_exception, expected",
        [
            pytest.param(ModuleNotFoundError, InvalidPluginError, id="ModuleNotFoundError"),
            pytest.param(ImportError, InvalidPluginError, id="ImportError"),
        ],
    )
    def test_check_precondition_raises(self, raise_exception: type[Exception], expected: type[Exception]) -> None:
        """Test the import error."""
        # Arrange
        plugin_manager = PluginManager()
        application = MagicMock(ApplicationAbstractProtocol)
        with patch(
            "fastapi_factory_utilities.core.app.plugin_manager.plugin_manager.PluginManager._import_module"
        ) as mock_import_module:
            mock_import_module.side_effect = raise_exception()
            # Assert
            with pytest.raises(expected_exception=expected):
                # Act
                plugin_manager._check_pre_conditions(  # pylint: disable=protected-access # pyright: ignore[reportPrivateUsage]
                    plugin_package="",
                    want_to_activate_plugins=cast(list[PluginsEnum], [self.PluginsEnumForTest.INVALID_PLUGIN]),
                    application=application,
                )

    def test_successfull_load_of_plugins(self) -> None:
        """Test the successful load of a plugin."""
        # Arrange
        plugin_manager = PluginManager()
        application = MagicMock(ApplicationAbstractProtocol)
        plugin_mock = MagicMock(PluginProtocol)
        plugin_mock.on_load = MagicMock(return_value=[PluginState(key="test", value="test")])

        plugin_manager.add_application_context(application=application)
        with patch(
            "fastapi_factory_utilities.core.app.plugin_manager.plugin_manager.PluginManager._check_pre_conditions"
        ) as mock_import_module:
            mock_import_module.return_value = [plugin_mock]
            # Act
            plugin_manager.load()

        # Assert
        assert plugin_mock.on_load.called
        assert plugin_mock.on_load.call_count == 1

        assert len(plugin_manager.states) == 1
        assert plugin_manager.states[0].key == "test"
        assert plugin_manager.states[0].value == "test"

    @pytest.mark.asyncio
    async def test_successfull_trigger_of_plugins(self) -> None:
        """Test the successful trigger of a plugin."""
        # Arrange
        plugin_manager = PluginManager()
        application = MagicMock(ApplicationAbstractProtocol)
        plugin_mock = MagicMock(PluginProtocol)
        plugin_mock.on_startup = AsyncMock(return_value=[PluginState(key="startup", value="startup")])
        plugin_mock.on_shutdown = AsyncMock()

        plugin_manager.add_application_context(application=application)
        with patch(
            "fastapi_factory_utilities.core.app.plugin_manager.plugin_manager.PluginManager._check_pre_conditions"
        ) as mock_import_module:
            mock_import_module.return_value = [plugin_mock]
            plugin_manager.load()
            # Act
            await plugin_manager.trigger_startup()
            await plugin_manager.trigger_shutdown()

        # Assert\
        assert plugin_mock.on_startup.called
        assert plugin_mock.on_startup.call_count == 1
        assert plugin_mock.on_shutdown.called
        assert plugin_mock.on_shutdown.call_count == 1

        assert len(plugin_manager.states) == 1
        assert plugin_manager.states[0].value == "startup"
        assert plugin_manager.states[0].key == "startup"
