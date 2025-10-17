"""Cong Test."""

import logging

from fastapi_factory_utilities.core.utils.log import (
    LoggingConfig,
    LogModeEnum,
    setup_log,
)

from .fixtures.mongo import (
    mongodb_server_as_container,
    mongodb_async_database_from_container,
)

setup_log(
    mode=LogModeEnum.CONSOLE,
    log_level="DEBUG",
    logging_config=[
        LoggingConfig(
            name="pymongo",
            level=logging.INFO,
        ),
        LoggingConfig(name="pymongo", level=logging.INFO),
        LoggingConfig(name="mirakuru", level=logging.INFO),
        LoggingConfig(name="asyncio", level=logging.INFO),
    ],
)



__all__: list[str] = [
    "mongodb_server_as_container",
    "mongodb_async_database_from_container",
]
