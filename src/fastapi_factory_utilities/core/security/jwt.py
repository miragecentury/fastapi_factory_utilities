"""Provides security-related functions for the API."""

from asyncio import Task, TaskGroup
from http import HTTPStatus
from typing import Any, ClassVar, NewType, cast

import jwt
import pydantic
from fastapi import Request
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

Scope = NewType("Scope", str)


class JWTBearerDecoded(BaseModel):
    """JWT bearer token decoded."""

    model_config: ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
    )

    scopes: list[str] | None = None


class JWTBearerAuthentication:
    """JWT Bearer Authentication.

    This class is used to authenticate users using JWT tokens.
    It extracts the token from the request, decodes it, and verifies its validity.
    """

    def __init__(self, scopes: list[Scope] | None = None, jwt_raw: str | None = None) -> None:
        """Initialize the OAuth2 class.

        Args:
            scopes (SecurityScopes): Security scopes for the OAuth2.
            jwt_raw (str): JWT token to be used for authentication.
        """
        self.jwt_raw: str | None = jwt_raw
        self.scopes: list[Scope] | None = scopes

    def _extract_raw_token(self, request: Request) -> str:
        """Extract the raw token from the request.

        Args:
            request (Request): FastAPI request object.

        Returns:
            str: Raw token.

        Raises:
            HTTPException: If the token is missing or invalid.
        """
        try:
            authorization_header: str | None = request.headers.get("Authorization")
        except (AttributeError, KeyError) as e:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Missing Credentials") from e

        if not authorization_header:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Missing Credentials")

        if not authorization_header.startswith("Bearer "):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid Credentials")

        return authorization_header.split(sep=" ")[1]

    async def _decode_jwt(self, jwt_raw: str) -> JWTBearerDecoded:
        """Decode the JWT token.

        Args:
            jwt_raw (str): Raw JWT token.

        Returns:
            JWTBearerDecoded: Decoded JWT token.

        Raises:
            HTTPException: If the token is invalid or expired.
        """
        try:
            jwt_decoded: dict[str, Any] = cast(
                dict[str, Any],
                jwt.decode(
                    jwt=jwt_raw,
                    algorithms=["HS256", "RS256"],
                    options={"verify_signature": True},
                ),
            )
            return JWTBearerDecoded(**jwt_decoded)
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token expired") from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token") from e
        except pydantic.ValidationError as e:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail=f"Invalid token: {e.json()}") from e

    async def _verify(self, jwt_raw: str) -> None:
        """Verify the JWT token.

        Args:
            jwt_raw (str): Raw JWT token.
        """
        pass

    def _has_scope(self, jwt_decoded: JWTBearerDecoded) -> None:
        """Check if the JWT token has the required scope.

        Args:
            jwt_decoded (JWTBearerDecoded): Decoded JWT token.

        """
        # Just Authentication (no scopes, no authorization)
        if not self.scopes:
            return
        # JWT without scopes (no authorization)
        if not jwt_decoded.scopes:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Unauthorized")
        # Check if all required scopes are present
        if not all(scope in jwt_decoded.scopes for scope in (self.scopes or [])):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Unauthorized")

        # All scopes are valid (authorization)
        return

    async def __call__(self, request: Request | None = None) -> JWTBearerDecoded:
        """Call the JWT bearer authentication.

        Args:
            request (Request): FastAPI request object.

        Returns:
            JWTBearerDecoded: Decoded JWT token.

        Raises:
            HTTPException: If the token is missing or invalid.
        """
        # Ensure that the jwt will be provided
        # by the request or by the jwt parameter
        if self.jwt_raw is None and request is None:
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Missing Credentials")

        if self.jwt_raw is None:
            jwt_raw: str = self._extract_raw_token(request=request)  # type: ignore[arg-type]
        else:
            jwt_raw: str = self.jwt_raw

        # Execute the io bound and cpu bound tasks in parallel
        async with TaskGroup() as tg:
            # TODO: Can be disabled by configuration (for operation purposes)
            # Ensure that the jwt is not revoked or expired
            tg.create_task(self._verify(jwt_raw=jwt_raw), name="verify_jwt")
            # Ensure that the jwt is not altered or expired
            task_decode: Task[Any] = tg.create_task(self._decode_jwt(jwt_raw=jwt_raw), name="decode_jwt")
        # Scope Validation
        jwt_decoded: JWTBearerDecoded = task_decode.result()
        self._has_scope(jwt_decoded=jwt_decoded)
        return jwt_decoded
