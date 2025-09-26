"""FastAPI Factory Utilities exceptions."""

import logging
from collections.abc import Sequence
from typing import NotRequired, TypedDict, Unpack

from opentelemetry.trace import Span, get_current_span
from opentelemetry.util.types import AttributeValue
from structlog.stdlib import BoundLogger, get_logger

_logger: BoundLogger = get_logger()


class ExceptionParameters(TypedDict):
    """Parameters for the exception."""

    message: NotRequired[str]
    level: NotRequired[int]


class FastAPIFactoryUtilitiesError(Exception):
    """Base exception for the FastAPI Factory Utilities."""

    def __init__(
        self,
        *args: object,
        **kwargs: Unpack[ExceptionParameters],
    ) -> None:
        """Instantiate the exception.

        Args:
            *args: The arguments.
            message: The message.
            level: The logging level.
            **kwargs: The keyword arguments.

        """
        # Extract the message and the level from the kwargs if they are present
        self.message: str | None = kwargs.pop("message", None)
        self.level: int = kwargs.pop("level", logging.ERROR)

        # If the message is not present, try to extract it from the args
        if self.message is None and len(args) > 0 and isinstance(args[0], str):
            self.message = args[0]

        # Log the Exception
        if self.message:
            _logger.log(level=self.level, event=self.message)

        try:
            # Propagate the exception
            span: Span = get_current_span()
            # If not otel is setup, INVALID_SPAN is retrieved from get_current_span
            # and it will respond False to the is_recording method
            if span.is_recording():
                span.record_exception(self)
                for key, value in kwargs.items():
                    attribute_value: AttributeValue
                    if not isinstance(value, (str, bool, int, float, Sequence)):
                        attribute_value = str(value)
                    else:
                        attribute_value = value
                    span.set_attribute(key, attribute_value)
        except Exception:  # pylint: disable=broad-exception-caught
            # Suppress any errors that occur while propagating the exception
            pass

        # Call the parent class
        super().__init__(*args)

    def __str__(self) -> str:
        """Return the string representation of the exception.

        Returns:
            str: The message if available, otherwise the default exception string.
        """
        if self.message is not None:
            return self.message
        return super().__str__()
