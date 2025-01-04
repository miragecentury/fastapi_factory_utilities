"""Cong Test."""

import asyncio
import logging
import os
from collections.abc import AsyncGenerator, Generator
from typing import Any
from uuid import UUID, uuid4

import pytest
from mirakuru import TCPExecutor
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pytest_mongo import factories  # pyright: ignore[reportMissingTypeStubs]
from structlog.stdlib import get_logger
from testcontainers.mongodb import (  # pyright: ignore[reportMissingTypeStubs]
    MongoDbContainer,
)

from fastapi_factory_utilities.core.utils.log import (
    LoggingConfig,
    LogModeEnum,
    setup_log,
)

setup_log(
    mode=LogModeEnum.CONSOLE,
    logging_config=[
        LoggingConfig(name="pymongo", level=logging.INFO),
        LoggingConfig(name="mirakuru", level=logging.INFO),
        LoggingConfig(name="asyncio", level=logging.INFO),
    ],
)

_logger = get_logger(__package__)

CONNECTION_TIMEOUT: int = 100
SOCKET_TIMEOUT: int = 300

mongodb_with_flexible_executable = factories.mongo_proc(
    executable=os.getenv("MONGO_EXECUTABLE", "/usr/bin/mongod"),
)

setup_log(
    mode=LogModeEnum.CONSOLE,
    log_level="DEBUG",
    logging_config=[
        LoggingConfig(
            name="pymongo",
            level=logging.INFO,
        )
    ],
)


@pytest.fixture(scope="session")
def database_for_function(
    mongodb_with_flexible_executable: TCPExecutor,  # pylint: disable=redefined-outer-name
) -> Generator[TCPExecutor, None, None]:
    """Cleanup the database.

    Args:
        mongodb_with_flexible_executable (TCPExecutor): The TCP executor for mongodb server.

    """
    yield mongodb_with_flexible_executable
    mongodb_with_flexible_executable.stop()


@pytest.fixture(scope="function")  # pyright: ignore
async def async_motor_database(
    database_for_function: TCPExecutor,  # pylint: disable=redefined-outer-name
) -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    """Create an async motor database.

    Args:
        database_for_function (TCPExecutor): The TCP executor for mongodb server.

    Yields:
        Generator[AsyncIOMotorDatabase, None, None]: The async motor database.

    """
    _logger.debug(
        f"Creating AsyncIOMotorDatabase with " f"{database_for_function.host=} and " f"{database_for_function.port=}"
    )
    client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(
        host=f"mongodb://{database_for_function.host}:{database_for_function.port}",
        serverMonitoringMode="stream",  # prevent error on teardown of the client
        connectTimeoutMS=CONNECTION_TIMEOUT,
        socketTimeoutMS=SOCKET_TIMEOUT,
        timeoutMS=SOCKET_TIMEOUT,
        serverSelectionTimeoutMS=CONNECTION_TIMEOUT,
    )
    database_name = str(uuid4())
    database: AsyncIOMotorDatabase[Any] = client.get_database(name=database_name)

    try:
        yield database
    finally:
        await client.drop_database(name_or_database=database_name)
        client.close()
        # Pymongo does not cleanely close the connection
        # the monitoring stream is still running
        # and need time to close nicely
        # so we wait a bit to prevent the exception and log message
        await asyncio.sleep(0.3)


MAX_TRIES: int = 10


@pytest.fixture(scope="session")
def mongodb_server_as_container() -> Generator[MongoDbContainer, None, None]:
    """Start the mongodb server."""
    mongodb_container: MongoDbContainer = MongoDbContainer(
        "mongo:latest",
        port=27017,
    )
    if not mongodb_container:
        raise Exception(  # pylint: disable=broad-exception-raised
            "Could not find a random port for the mongodb server."
        )

    mongodb_container.start()
    yield mongodb_container
    mongodb_container.stop(delete_volume=True)


@pytest.fixture(scope="function")
async def mongodb_async_database_from_container(
    mongodb_server_as_container: MongoDbContainer,  # pylint: disable=redefined-outer-name
) -> AsyncGenerator[AsyncIOMotorDatabase[Any], None]:
    """Create an async motor database."""
    exposed_port: int | None = int(mongodb_server_as_container.get_exposed_port(27017))
    exposed_port = exposed_port if exposed_port else 27017
    username: str = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "test")
    password: str = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "test")
    mongodb_client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(
        host=mongodb_server_as_container.get_container_host_ip(),
        port=exposed_port,
        connect=True,
        username=username,
        password=password,
    )
    database_name: UUID = uuid4()
    mongodb_database: AsyncIOMotorDatabase[Any] = AsyncIOMotorDatabase(mongodb_client, str(database_name))

    yield mongodb_database

    await mongodb_client.drop_database(str(database_name))
    mongodb_client.close()
