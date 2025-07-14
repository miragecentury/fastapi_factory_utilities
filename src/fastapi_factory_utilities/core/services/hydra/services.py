"""Provides a service to interact with the Hydra service."""

from base64 import b64encode
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

from .exceptions import HydraOperationError, HydraTokenInvalidError
from .objects import HydraTokenIntrospectObject


class HydraService:
    """Service to interact with the Hydra service."""

    INTROSPECT_ENDPOINT: str = "/admin/oauth2/introspect"
    CLIENT_CREDENTIALS_ENDPOINT: str = "/oauth2/token"

    def __init__(
        self,
        hydra_admin_http_config: HttpServiceDependencyConfig,
        hydra_public_http_config: HttpServiceDependencyConfig,
    ) -> None:
        """Instanciate the Hydra service.

        Args:
            hydra_admin_http_config (HttpServiceDependencyConfig): The Hydra admin HTTP configuration.
            hydra_public_http_config (HttpServiceDependencyConfig): The Hydra public HTTP configuration.
        """
        self._hydra_admin_http_config: HttpServiceDependencyConfig = hydra_admin_http_config
        self._hydra_public_http_config: HttpServiceDependencyConfig = hydra_public_http_config

    async def introspect(self, token: str) -> HydraTokenIntrospectObject:
        """Introspects a token using the Hydra service.

        Args:
            token (str): The token to introspect.

        Raises:
            HydraOperationError: If the introspection fails.
            HydraTokenInvalidError: If the token is invalid.
        """
        async with aiohttp.ClientSession(
            base_url=str(self._hydra_admin_http_config.url),
        ) as session:
            async with session.post(
                url=self.INTROSPECT_ENDPOINT,
                data={"token": token},
            ) as response:
                if response.status != HTTPStatus.OK:
                    raise HydraTokenInvalidError()

                try:
                    instrospect: HydraTokenIntrospectObject = HydraTokenIntrospectObject(**await response.json())
                except ValidationError as error:
                    raise HydraOperationError() from error

                return instrospect

    async def oauth2_client_credentials(self, client_id: str, client_secret: str, scope: str) -> str:
        """Get the OAuth2 client credentials.

        Args:
            client_id (str): The client ID.
            client_secret (str): The client secret.
            scope (str): The scope.

        Returns:
            str: The access token.

        Raises:
            HydraOperationError: If the client credentials request fails.
        """
        # Create base64 encoded Basic Auth header
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = b64encode(auth_bytes).decode("utf-8")

        async with aiohttp.ClientSession(
            base_url=str(self._hydra_public_http_config.url),
        ) as session:
            async with session.post(
                url=self.CLIENT_CREDENTIALS_ENDPOINT,
                headers={"Authorization": f"Basic {auth_b64}"},
                data={"grant_type": "client_credentials", "scope": scope},
            ) as response:
                response_data = await response.json()
                if response.status != HTTPStatus.OK:
                    raise HydraOperationError(f"Failed to get client credentials: {response_data}")

                return response_data["access_token"]


def depends_hydra_service(
    dependency_config: Annotated[DependencyConfig, Depends(depends_dependency_config)],
) -> HydraService:
    """Dependency injection for the Hydra service.

    Args:
        dependency_config (DependencyConfig): The dependency configuration.

    Returns:
        HydraService: The Hydra service instance.

    Raises:
        HydraOperationError: If the Hydra admin or public dependency is not configured.
    """
    if dependency_config.hydra_admin is None or dependency_config.hydra_public is None:
        raise HydraOperationError(message="Hydra admin or public dependency not configured")

    return HydraService(
        hydra_admin_http_config=dependency_config.hydra_admin,
        hydra_public_http_config=dependency_config.hydra_public,
    )
