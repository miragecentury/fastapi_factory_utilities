"""FastAPI Factory Utilities exceptions."""

import logging

from structlog.stdlib import BoundLogger, get_logger

_logger: BoundLogger = get_logger()


class FastAPIFactoryUtilitiesError(Exception):
    """Base exception for the FastAPI Factory Utilities."""

    def __init__(
        self,
        *args: object,
        message: str | None = None,
        level: int = logging.ERROR,
    ) -> None:
        """Instanciate the exception."""
        if message:
            _logger.log(level=level, event=message)
            args = (message, *args)
        super().__init__(*args)
