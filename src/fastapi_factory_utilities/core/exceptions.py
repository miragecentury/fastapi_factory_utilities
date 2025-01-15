"""FastAPI Factory Utilities exceptions."""

import logging
from typing import Any

from opentelemetry.trace import Span, get_current_span
from structlog.stdlib import BoundLogger, get_logger

_logger: BoundLogger = get_logger()


class FastAPIFactoryUtilitiesError(Exception):
    """Base exception for the FastAPI Factory Utilities."""

    def __init__(
        self,
        *args: tuple[Any],
        message: str | None = None,
        level: int = logging.ERROR,
        **kwargs: dict[str, Any],
    ) -> None:
        """Instanciate the exception.

        Args:
            *args (Tuple[Any]): The arguments.
            message (str | None): The message.
            level (int): The logging level.
            **kwargs (dict[str, Any]): The keyword arguments
        """
        # Log the Exception
        if message:
            _logger.log(level=level, event=message)
            self.message = message
            self.level = level
            args = (message, *args)  # type: ignore
        # Propagate the exception
        span: Span = get_current_span()
        # If not otel is setup, INVALID_SPAN is retrive from get_current_span
        # and it will respond False to the is_recording method
        if span.is_recording():
            span.record_exception(self)
        # Call the parent class
        super().__init__(*args, **kwargs)
