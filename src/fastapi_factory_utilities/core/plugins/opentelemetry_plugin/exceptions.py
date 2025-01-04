"""Provides the exceptions for the OpenTelemetryPlugin."""


class OpenTelemetryPluginBaseException(BaseException):
    """Base exception for the OpenTelemetryPlugin."""

    pass


class OpenTelemetryPluginConfigError(OpenTelemetryPluginBaseException):
    """Exception for the OpenTelemetryPlugin configuration."""

    pass
