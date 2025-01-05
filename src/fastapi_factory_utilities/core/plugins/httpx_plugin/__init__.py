"""Httpx Plugin Module."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi_factory_utilities.core.app.plugin_manager.plugin_state import (
        PluginState,
    )
    from fastapi_factory_utilities.core.protocols import BaseApplicationProtocol


def pre_conditions_check(application: "BaseApplicationProtocol") -> bool:  # pylint: disable=unused-argument
    """Check the pre-conditions for the example plugin."""
    return True


def on_load(
    application: "BaseApplicationProtocol",  # pylint: disable=unused-argument
) -> list["PluginState"] | None:
    """Actions to perform on load for the example plugin."""
    return


async def on_startup(
    application: "BaseApplicationProtocol",  # pylint: disable=unused-argument
) -> list["PluginState"] | None:
    """Actions to perform on startup for the example plugin."""
    return


async def on_shutdown(application: "BaseApplicationProtocol") -> None:  # pylint: disable=unused-argument
    """Actions to perform on shutdown for the example plugin."""
    return
