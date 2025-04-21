"""Provides the KratosService class for handling Kratos operations."""

from http import HTTPStatus
from typing import Annotated

import aiohttp
from fastapi import Depends
from pydantic import ValidationError

from fastapi_factory_utilities.core.app import (
    DependencyConfig,
    HttpServiceDependencyConfig,
    depends_dependency_config,
)

from .exceptions import KratosOperationError, KratosSessionInvalidError
from .objects import KratosSessionObject


class KratosService:
    """Service class for handling Kratos operations."""

    COOKIE_NAME: str = "ory_kratos_session"

    def __init__(self, kratos_http_config: HttpServiceDependencyConfig) -> None:
        """Initialize the KratosService class.

        Args:
            kratos_http_config (HttpServiceDependencyConfig): Kratos HTTP configuration.
        """
        self._http_config: HttpServiceDependencyConfig = kratos_http_config

    async def whoami(self, cookie_value: str) -> KratosSessionObject:
        """Get the current user session.

        Args:
            cookie_value (str): Cookie value.

        Returns:
            KratosSessionObject: Kratos session object.

        Raises:
            KratosOperationError: If the Kratos service returns an error.
            KratosSessionInvalidError: If the Kratos session is invalid.
        """
        cookies: dict[str, str] = {self.COOKIE_NAME: cookie_value}
        async with aiohttp.ClientSession(base_url=str(self._http_config.url), cookies=cookies) as session:
            async with session.get(
                url="/sessions/whoami",
            ) as response:
                if response.status >= HTTPStatus.INTERNAL_SERVER_ERROR.value:
                    raise KratosOperationError(message=f"Kratos service error: {response.status} - {response.reason}")
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise KratosSessionInvalidError(
                        message=f"Kratos session invalid: {response.status} - {response.reason}"
                    )
                if response.status != HTTPStatus.OK:
                    raise KratosOperationError(message=f"Kratos service error: {response.status} - {response.reason}")

                try:
                    kratos_session: KratosSessionObject = KratosSessionObject(**await response.json())
                except ValidationError as e:
                    raise KratosOperationError(message=f"Kratos service error: {e}") from e

                return kratos_session


def depends_kratos_service(
    dependency_config: Annotated[DependencyConfig, Depends(depends_dependency_config)],
) -> KratosService:
    """Dependency function to get the Kratos service instance.

    Args:
        dependency_config (DependencyConfig): Dependency configuration.

    Returns:
        KratosService: Kratos service instance.

    Raises:
        KratosOperationError: If the Kratos dependency is not configured.
    """
    if dependency_config.kratos is None:
        raise KratosOperationError(message="Kratos dependency not configured")
    return KratosService(
        kratos_http_config=dependency_config.kratos,
    )
