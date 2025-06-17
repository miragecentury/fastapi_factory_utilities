"""Provide Kratos Session and Identity classes."""

from enum import StrEnum
from typing import Annotated

from fastapi import Depends, HTTPException, Request

from fastapi_factory_utilities.core.services.kratos import (
    KratosOperationError,
    KratosService,
    KratosSessionInvalidError,
    KratosSessionObject,
    depends_kratos_service,
)


class KratosSessionAuthenticationErrors(StrEnum):
    """Kratos Session Authentication Errors."""

    MISSING_CREDENTIALS = "Missing Credentials"
    INVALID_CREDENTIALS = "Invalid Credentials"
    INTERNAL_SERVER_ERROR = "Internal Server Error"


class KratosSessionAuthentication:
    """Kratos Session class."""

    DEFAULT_COOKIE_NAME: str = "ory_kratos_session"

    def __init__(self, cookie_name: str = DEFAULT_COOKIE_NAME, raise_exception: bool = True) -> None:
        """Initialize the KratosSessionAuthentication class.

        Args:
            cookie_name (str): Name of the cookie to extract the session
            raise_exception (bool): Whether to raise an exception or return None
        """
        self._cookie_name: str = cookie_name
        self._raise_exception: bool = raise_exception

    def _extract_cookie(self, request: Request) -> str | None:
        """Extract the cookie from the request.

        Args:
            request (Request): FastAPI request object.

        Returns:
            str | None: Cookie value or None if not found.

        Raises:
            HTTPException: If the cookie is missing.
        """
        return request.cookies.get(self._cookie_name, None)

    async def __call__(
        self, request: Request, kratos_service: Annotated[KratosService, Depends(depends_kratos_service)]
    ) -> KratosSessionObject | KratosSessionAuthenticationErrors:
        """Extract the Kratos session from the request.

        Args:
            request (Request): FastAPI request object.
            kratos_service (KratosService): Kratos service object.

        Returns:
            KratosSessionObject | KratosSessionAuthenticationErrors: Kratos session object or error.

        Raises:
            HTTPException: If the session is invalid and raise_exception is True.
        """
        cookie: str | None = self._extract_cookie(request)
        if not cookie:
            if self._raise_exception:
                raise HTTPException(
                    status_code=401,
                    detail=KratosSessionAuthenticationErrors.MISSING_CREDENTIALS,
                )
            else:
                return KratosSessionAuthenticationErrors.MISSING_CREDENTIALS

        try:
            session: KratosSessionObject = await kratos_service.whoami(cookie_value=cookie)
        except KratosSessionInvalidError as e:
            if self._raise_exception:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid Credentials",
                ) from e
            else:
                return KratosSessionAuthenticationErrors.INVALID_CREDENTIALS
        except KratosOperationError as e:
            if self._raise_exception:
                raise HTTPException(
                    status_code=500,
                    detail="Internal Server Error",
                ) from e
            else:
                return KratosSessionAuthenticationErrors.INTERNAL_SERVER_ERROR

        return session
