"""Provide Kratos Session and Identity classes."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request

from fastapi_factory_utilities.core.services.kratos import (
    KratosOperationError,
    KratosService,
    KratosSessionInvalidError,
    KratosSessionObject,
    depends_kratos_service,
)


class KratosSessionAuthentication:
    """Kratos Session class."""

    DEFAULT_COOKIE_NAME: str = "ory_kratos_session"

    def __init__(self, cookie_name: str = DEFAULT_COOKIE_NAME) -> None:
        """Initialize the KratosSessionAuthentication class.

        Args:
            cookie_name (str): Name of the cookie to extract the session
        """
        self._cookie_name: str = cookie_name

    def _extract_cookie(self, request: Request) -> str:
        """Extract the cookie from the request.

        Args:
            request (Request): FastAPI request object.

        Returns:
            str | None: Cookie value or None if not found.

        Raises:
            HTTPException: If the cookie is missing.
        """
        cookie: str | None = request.cookies.get(self._cookie_name)
        if not cookie:
            raise HTTPException(
                status_code=401,
                detail="Missing Credentials",
            )
        return cookie

    async def __call__(
        self, request: Request, kratos_service: Annotated[KratosService, Depends(depends_kratos_service)]
    ) -> KratosSessionObject:
        """Extract the Kratos session from the request.

        Args:
            request (Request): FastAPI request object.
            kratos_service (KratosService): Kratos service object.

        Returns:
            KratosSessionObject: Kratos session object.

        Raises:
            HTTPException: If the session is invalid.
        """
        cookie: str = self._extract_cookie(request)
        try:
            session: KratosSessionObject = await kratos_service.whoami(cookie_value=cookie)
        except KratosSessionInvalidError as e:
            raise HTTPException(
                status_code=401,
                detail="Invalid Credentials",
            ) from e
        except KratosOperationError as e:
            raise HTTPException(
                status_code=500,
                detail="Internal Server Error",
            ) from e

        return session
