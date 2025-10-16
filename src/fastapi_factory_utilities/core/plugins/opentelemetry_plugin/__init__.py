"""OpenTelemetry Plugin Module."""

from .configs import OpenTelemetryConfig, OpenTelemetryMeterConfig, OpenTelemetryTracerConfig
from .exceptions import OpenTelemetryPluginBaseException, OpenTelemetryPluginConfigError
from .plugins import OpenTelemetryPlugin, depends_meter_provider, depends_otel_config, depends_tracer_provider

__all__: list[str] = [
    "OpenTelemetryConfig",
    "OpenTelemetryMeterConfig",
    "OpenTelemetryPlugin",
    "OpenTelemetryPluginBaseException",
    "OpenTelemetryPluginConfigError",
    "OpenTelemetryTracerConfig",
    "depends_meter_provider",
    "depends_otel_config",
    "depends_tracer_provider",
]
