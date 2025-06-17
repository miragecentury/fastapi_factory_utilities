"""OpenTelemetry Plugin Module."""

import asyncio
from typing import cast

from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import (  # pyright: ignore[reportMissingTypeStubs]
    FastAPIInstrumentor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from structlog.stdlib import BoundLogger, get_logger

from fastapi_factory_utilities.core.protocols import ApplicationAbstractProtocol

from .builder import OpenTelemetryPluginBuilder
from .configs import OpenTelemetryConfig
from .exceptions import OpenTelemetryPluginBaseException, OpenTelemetryPluginConfigError

__all__: list[str] = [
    "OpenTelemetryConfig",
    "OpenTelemetryPluginBaseException",
    "OpenTelemetryPluginConfigError",
    "OpenTelemetryPluginBuilder",
]

_logger: BoundLogger = get_logger()


def pre_conditions_check(application: ApplicationAbstractProtocol) -> bool:
    """Check the pre-conditions for the OpenTelemetry plugin.

    Args:
        application (BaseApplicationProtocol): The application.

    Returns:
        bool: True if the pre-conditions are met, False otherwise.
    """
    del application
    return True


def on_load(
    application: ApplicationAbstractProtocol,
) -> None:
    """Actions to perform on load for the OpenTelemetry plugin.

    Args:
        application (BaseApplicationProtocol): The application.
    """
    # Build the OpenTelemetry Resources, TracerProvider and MeterProvider
    try:
        otel_builder: OpenTelemetryPluginBuilder = OpenTelemetryPluginBuilder(application=application).build_all()
    except OpenTelemetryPluginBaseException as exception:
        _logger.error(f"OpenTelemetry plugin failed to start. {exception}")
        return
    # Configuration is never None at this point (checked in the builder and raises an exception)
    otel_config: OpenTelemetryConfig = cast(OpenTelemetryConfig, otel_builder.config)
    # Save as state in the FastAPI application
    application.get_asgi_app().state.tracer_provider = otel_builder.tracer_provider
    application.get_asgi_app().state.meter_provider = otel_builder.meter_provider
    application.get_asgi_app().state.otel_config = otel_config
    # Instrument the FastAPI application
    FastAPIInstrumentor.instrument_app(  # pyright: ignore[reportUnknownMemberType]
        app=application.get_asgi_app(),
        tracer_provider=otel_builder.tracer_provider,
        meter_provider=otel_builder.meter_provider,
        excluded_urls=otel_config.excluded_urls,
    )
    # Instrument the AioHttpClient
    AioHttpClientInstrumentor().instrument(  # pyright: ignore[reportUnknownMemberType]
        tracer_provider=otel_builder.tracer_provider,
        meter_provider=otel_builder.meter_provider,
    )

    _logger.debug(f"OpenTelemetry plugin loaded. {otel_config.activate=}")


async def on_startup(
    application: ApplicationAbstractProtocol,
) -> None:
    """Actions to perform on startup for the OpenTelemetry plugin.

    Args:
        application (BaseApplicationProtocol): The application.

    Returns:
        None
    """
    del application
    _logger.debug("OpenTelemetry plugin started.")


async def on_shutdown(application: ApplicationAbstractProtocol) -> None:
    """Actions to perform on shutdown for the OpenTelemetry plugin.

    Args:
        application (BaseApplicationProtocol): The application.

    Returns:
        None
    """
    tracer_provider: TracerProvider = application.get_asgi_app().state.tracer_provider
    meter_provider: MeterProvider = application.get_asgi_app().state.meter_provider
    otel_config: OpenTelemetryConfig = application.get_asgi_app().state.otel_config

    seconds_to_ms_multiplier: int = 1000

    async def close_tracer_provider() -> None:
        """Close the tracer provider."""
        tracer_provider.force_flush(timeout_millis=otel_config.closing_timeout * seconds_to_ms_multiplier)
        # No Delay for the shutdown of the tracer provider
        tracer_provider.shutdown()

    async def close_meter_provider() -> None:
        """Close the meter provider.

        Split the timeout in half for the flush and shutdown.
        """
        meter_provider.force_flush(timeout_millis=int(otel_config.closing_timeout / 2) * seconds_to_ms_multiplier)
        meter_provider.shutdown(timeout_millis=int(otel_config.closing_timeout / 2) * seconds_to_ms_multiplier)

    _logger.debug("OpenTelemetry plugin stop requested. Flushing and closing...")

    await asyncio.gather(
        close_tracer_provider(),
        close_meter_provider(),
    )

    _logger.debug("OpenTelemetry plugin closed.")
