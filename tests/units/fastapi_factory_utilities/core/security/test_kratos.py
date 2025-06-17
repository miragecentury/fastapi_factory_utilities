"""Unit tests for the Kratos session authentication."""

from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, Request

from fastapi_factory_utilities.core.security.kratos import (
    KratosSessionAuthentication,
    KratosSessionAuthenticationErrors,
)
from fastapi_factory_utilities.core.services.kratos import (
    KratosOperationError,
    KratosService,
    KratosSessionInvalidError,
    KratosSessionObject,
)


class TestKratosSessionAuthentication:
    """Test cases for KratosSessionAuthentication class."""

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock request with cookies.

        Returns:
            MagicMock: A mock request object.
        """
        request = MagicMock(spec=Request)
        request.cookies = {}
        return request

    @pytest.fixture
    def mock_kratos_service(self) -> AsyncMock:
        """Create a mock KratosService.

        Returns:
            AsyncMock: A mock KratosService object.
        """
        return AsyncMock(spec=KratosService)

    @pytest.fixture
    def session_auth(self) -> KratosSessionAuthentication:
        """Create a KratosSessionAuthentication instance.

        Returns:
            KratosSessionAuthentication: A KratosSessionAuthentication instance.
        """
        return KratosSessionAuthentication()

    def test_init_with_default_values(self) -> None:
        """Test initialization with default values."""
        auth = KratosSessionAuthentication()
        assert auth._cookie_name == "ory_kratos_session"
        assert auth._raise_exception is True

    def test_init_with_custom_values(self) -> None:
        """Test initialization with custom values."""
        auth = KratosSessionAuthentication(cookie_name="custom_cookie", raise_exception=False)
        assert auth._cookie_name == "custom_cookie"
        assert auth._raise_exception is False

    def test_extract_cookie_when_cookie_exists(self, mock_request: MagicMock) -> None:
        """Test cookie extraction when cookie exists.

        Args:
            mock_request (MagicMock): Mock request object.
        """
        mock_request.cookies = {"ory_kratos_session": "test_cookie"}
        auth = KratosSessionAuthentication()
        cookie = auth._extract_cookie(mock_request)
        assert cookie == "test_cookie"

    def test_extract_cookie_when_cookie_missing(self, mock_request: MagicMock) -> None:
        """Test cookie extraction when cookie is missing.

        Args:
            mock_request (MagicMock): Mock request object.
        """
        auth = KratosSessionAuthentication()
        cookie = auth._extract_cookie(mock_request)
        assert cookie is None

    @pytest.mark.asyncio
    async def test_call_with_valid_session(
        self,
        mock_request: MagicMock,
        mock_kratos_service: AsyncMock,
        session_auth: KratosSessionAuthentication,
    ) -> None:
        """Test successful session validation.

        Args:
            mock_request (MagicMock): Mock request object.
            mock_kratos_service (AsyncMock): Mock KratosService object.
            session_auth (KratosSessionAuthentication): KratosSessionAuthentication instance.
        """
        mock_request.cookies = {"ory_kratos_session": "valid_cookie"}
        mock_session = MagicMock(spec=KratosSessionObject)
        mock_kratos_service.whoami.return_value = mock_session

        result = await session_auth(mock_request, mock_kratos_service)

        assert result == mock_session
        mock_kratos_service.whoami.assert_called_once_with(cookie_value="valid_cookie")

    @pytest.mark.asyncio
    async def test_call_with_missing_cookie_raise_exception(
        self,
        mock_request: MagicMock,
        mock_kratos_service: AsyncMock,
        session_auth: KratosSessionAuthentication,
    ) -> None:
        """Test behavior when cookie is missing and raise_exception is True.

        Args:
            mock_request (MagicMock): Mock request object.
            mock_kratos_service (AsyncMock): Mock KratosService object.
            session_auth (KratosSessionAuthentication): KratosSessionAuthentication instance.
        """
        with pytest.raises(HTTPException) as exc_info:
            await session_auth(mock_request, mock_kratos_service)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == KratosSessionAuthenticationErrors.MISSING_CREDENTIALS

    @pytest.mark.asyncio
    async def test_call_with_missing_cookie_no_raise(
        self,
        mock_request: MagicMock,
        mock_kratos_service: AsyncMock,
    ) -> None:
        """Test behavior when cookie is missing and raise_exception is False.

        Args:
            mock_request (MagicMock): Mock request object.
            mock_kratos_service (AsyncMock): Mock KratosService object.
        """
        auth = KratosSessionAuthentication(raise_exception=False)
        result = await auth(mock_request, mock_kratos_service)

        assert result == KratosSessionAuthenticationErrors.MISSING_CREDENTIALS

    @pytest.mark.asyncio
    async def test_call_with_invalid_session_raise_exception(
        self,
        mock_request: MagicMock,
        mock_kratos_service: AsyncMock,
        session_auth: KratosSessionAuthentication,
    ) -> None:
        """Test behavior when session is invalid and raise_exception is True.

        Args:
            mock_request (MagicMock): Mock request object.
            mock_kratos_service (AsyncMock): Mock KratosService object.
            session_auth (KratosSessionAuthentication): KratosSessionAuthentication instance.
        """
        mock_request.cookies = {"ory_kratos_session": "invalid_cookie"}
        mock_kratos_service.whoami.side_effect = KratosSessionInvalidError()

        with pytest.raises(HTTPException) as exc_info:
            await session_auth(mock_request, mock_kratos_service)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert exc_info.value.detail == "Invalid Credentials"

    @pytest.mark.asyncio
    async def test_call_with_invalid_session_no_raise(
        self,
        mock_request: MagicMock,
        mock_kratos_service: AsyncMock,
    ) -> None:
        """Test behavior when session is invalid and raise_exception is False.

        Args:
            mock_request (MagicMock): Mock request object.
            mock_kratos_service (AsyncMock): Mock KratosService object.
        """
        auth = KratosSessionAuthentication(raise_exception=False)
        mock_request.cookies = {"ory_kratos_session": "invalid_cookie"}
        mock_kratos_service.whoami.side_effect = KratosSessionInvalidError()

        result = await auth(mock_request, mock_kratos_service)

        assert result == KratosSessionAuthenticationErrors.INVALID_CREDENTIALS

    @pytest.mark.asyncio
    async def test_call_with_operation_error_raise_exception(
        self,
        mock_request: MagicMock,
        mock_kratos_service: AsyncMock,
        session_auth: KratosSessionAuthentication,
    ) -> None:
        """Test behavior when operation error occurs and raise_exception is True.

        Args:
            mock_request (MagicMock): Mock request object.
            mock_kratos_service (AsyncMock): Mock KratosService object.
            session_auth (KratosSessionAuthentication): KratosSessionAuthentication instance.
        """
        mock_request.cookies = {"ory_kratos_session": "valid_cookie"}
        mock_kratos_service.whoami.side_effect = KratosOperationError()

        with pytest.raises(HTTPException) as exc_info:
            await session_auth(mock_request, mock_kratos_service)

        assert exc_info.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Internal Server Error"

    @pytest.mark.asyncio
    async def test_call_with_operation_error_no_raise(
        self,
        mock_request: MagicMock,
        mock_kratos_service: AsyncMock,
    ) -> None:
        """Test behavior when operation error occurs and raise_exception is False.

        Args:
            mock_request (MagicMock): Mock request object.
            mock_kratos_service (AsyncMock): Mock KratosService object.
        """
        auth = KratosSessionAuthentication(raise_exception=False)
        mock_request.cookies = {"ory_kratos_session": "valid_cookie"}
        mock_kratos_service.whoami.side_effect = KratosOperationError()

        result = await auth(mock_request, mock_kratos_service)

        assert result == KratosSessionAuthenticationErrors.INTERNAL_SERVER_ERROR
