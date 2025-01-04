"""Test the setup.log module."""

from unittest.mock import MagicMock, patch

from fastapi_factory_utilities.core.utils.log import setup_log


class TestSetupLog:
    """Various tests for the setup_log function."""

    @patch("structlog.configure")
    def test_structlog_has_been_configured(self, structlog_configure_mock: MagicMock) -> None:
        """Test that structlog has been configured.

        Args:
            structlog_configure_mock (MagicMock): The structlog.configure mock.
        """
        setup_log()

        # Called once and only once
        assert structlog_configure_mock.called
        assert structlog_configure_mock.call_count == 1
