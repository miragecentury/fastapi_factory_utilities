"""Instruments for the OpenTelemetry plugin."""

# pyright: reportMissingTypeStubs=false

from collections.abc import Callable
from importlib.util import find_spec
from typing import Any

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider

from fastapi_factory_utilities.core.plugins.opentelemetry_plugin.configs import OpenTelemetryConfig
from fastapi_factory_utilities.core.protocols import ApplicationAbstractProtocol


def instrument_fastapi(
    application: ApplicationAbstractProtocol,
    config: OpenTelemetryConfig,
    meter_provider: MeterProvider,
    tracer_provider: TracerProvider,
) -> None:
    """Instrument the FastAPI application."""
    if find_spec(name="fastapi") and find_spec(name="opentelemetry.instrumentation.fastapi"):
        from opentelemetry.instrumentation.fastapi import (  # pylint: disable=import-outside-toplevel # noqa: PLC0415
            FastAPIInstrumentor,
        )

        excluded_urls_str: str | None = None if len(config.excluded_urls) == 0 else ",".join(config.excluded_urls)
        FastAPIInstrumentor.instrument_app(  # pyright: ignore[reportUnknownMemberType]
            app=application.get_asgi_app(),
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
            excluded_urls=excluded_urls_str,
        )


def instrument_aiohttp(
    application: ApplicationAbstractProtocol,  # pylint: disable=unused-argument
    config: OpenTelemetryConfig,  # pylint: disable=unused-argument
    meter_provider: MeterProvider,
    tracer_provider: TracerProvider,
) -> None:
    """Instrument the Aiohttp application.

    Args:
        application (ApplicationAbstractProtocol): The application.
        config (OpenTelemetryConfig): The configuration.
        meter_provider (MeterProvider): The meter provider.
        tracer_provider (TracerProvider): The tracer provider.

    Returns:
        None
    """
    if find_spec(name="aiohttp") and find_spec(name="opentelemetry.instrumentation.aiohttp_client"):
        from opentelemetry.instrumentation.aiohttp_client import (  # pylint: disable=import-outside-toplevel # noqa: PLC0415
            AioHttpClientInstrumentor,
        )

        AioHttpClientInstrumentor().instrument(  # pyright: ignore[reportUnknownMemberType]
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
        )


def instrument_aio_pika(
    application: ApplicationAbstractProtocol,  # pylint: disable=unused-argument
    config: OpenTelemetryConfig,  # pylint: disable=unused-argument
    meter_provider: MeterProvider,
    tracer_provider: TracerProvider,
) -> None:
    """Instrument the AioPika application."""
    if find_spec(name="aio_pika") and find_spec(name="opentelemetry.instrumentation.aio_pika"):
        from opentelemetry.instrumentation.aio_pika import (  # pylint: disable=import-outside-toplevel # noqa: PLC0415
            AioPikaInstrumentor,
        )

        AioPikaInstrumentor().instrument(  # pyright: ignore[reportUnknownMemberType]
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
        )


INSTRUMENTS: list[Callable[..., Any]] = [instrument_fastapi, instrument_aiohttp, instrument_aio_pika]

__all__: list[str] = ["INSTRUMENTS"]
