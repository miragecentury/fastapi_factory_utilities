"""
OpenTelemetry Plugin Module
"""

from injector import Module

from python_factory.core.app.base.protocols import BaseApplicationProtocol

from .configs import OpenTelemetryConfig
from .exceptions import OpenTelemetryPluginBaseException, OpenTelemetryPluginConfigError
from .providers import OpenTelemetryPluginModule

__all__: list[str] = [
    "OpenTelemetryConfig",
    "OpenTelemetryPluginBaseException",
    "OpenTelemetryPluginConfigError",
    "OpenTelemetryPluginModule",
]

INJECTOR_MODULE: type[Module] = OpenTelemetryPluginModule


def pre_conditions_check(application: BaseApplicationProtocol) -> bool:
    """
    Check the pre-conditions for the OpenTelemetry plugin.
    """
    del application
    return True


async def on_startup(application: BaseApplicationProtocol) -> None:
    """
    Actions to perform on startup for the OpenTelemetry plugin.
    """
    del application


async def on_shutdown(application: BaseApplicationProtocol) -> None:
    """
    Actions to perform on shutdown for the OpenTelemetry plugin.
    """
    del application