"""Tests for FastAPI Factory Utilities exceptions."""

import logging
from unittest.mock import Mock, patch

from opentelemetry.trace import INVALID_SPAN

from fastapi_factory_utilities.core.exceptions import FastAPIFactoryUtilitiesError


class TestFastAPIFactoryUtilitiesError:
    """Test cases for FastAPIFactoryUtilitiesError class."""

    def test_init_with_message_kwarg(self) -> None:
        """Test exception initialization with message as keyword argument."""
        message = "Test error message"
        level = logging.WARNING

        with patch("fastapi_factory_utilities.core.exceptions._logger") as mock_logger:
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError(message=message, level=level)

                assert exception.message == message
                assert exception.level == level
                mock_logger.log.assert_called_once_with(level=level, event=message)

    def test_init_with_message_in_args(self) -> None:
        """Test exception initialization with message as first positional argument."""
        message = "Test error message"

        with patch("fastapi_factory_utilities.core.exceptions._logger") as mock_logger:
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError(message)

                assert exception.message == message
                assert exception.level == logging.ERROR  # Default level
                mock_logger.log.assert_called_once_with(level=logging.ERROR, event=message)

    def test_init_with_default_level(self) -> None:
        """Test exception initialization with default logging level."""
        message = "Test error message"

        with patch("fastapi_factory_utilities.core.exceptions._logger") as mock_logger:
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError(message=message)

                assert exception.level == logging.ERROR
                mock_logger.log.assert_called_once_with(level=logging.ERROR, event=message)

    def test_init_without_message(self) -> None:
        """Test exception initialization without message."""
        with patch("fastapi_factory_utilities.core.exceptions._logger") as mock_logger:
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError()

                assert exception.message is None
                assert exception.level == logging.ERROR  # Default level
                mock_logger.log.assert_not_called()

    def test_init_with_non_string_first_arg(self) -> None:
        """Test exception initialization with non-string first positional argument."""
        with patch("fastapi_factory_utilities.core.exceptions._logger") as mock_logger:
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError(123, "additional arg")

                assert exception.message is None
                assert exception.level == logging.ERROR  # Default level
                mock_logger.log.assert_not_called()

    def test_init_with_empty_args(self) -> None:
        """Test exception initialization with empty positional arguments."""
        with patch("fastapi_factory_utilities.core.exceptions._logger") as mock_logger:
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError()

                assert exception.message is None
                assert exception.level == logging.ERROR  # Default level
                mock_logger.log.assert_not_called()

    def test_otel_span_recording_with_valid_span(self) -> None:
        """Test OpenTelemetry span recording when span is recording."""
        message = "Test error message"
        custom_attr = "custom_value"

        mock_span = Mock()
        mock_span.is_recording.return_value = True

        with patch("fastapi_factory_utilities.core.exceptions._logger"):
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_get_span:
                mock_get_span.return_value = mock_span

                exception = FastAPIFactoryUtilitiesError(
                    message=message,
                    custom_attr=custom_attr,  # type: ignore[call-arg]
                )

                mock_span.record_exception.assert_called_once_with(exception)
                mock_span.set_attribute.assert_called_once_with("custom_attr", custom_attr)

    def test_otel_span_recording_with_invalid_span(self) -> None:
        """Test OpenTelemetry span recording when span is not recording."""
        message = "Test error message"

        with patch("fastapi_factory_utilities.core.exceptions._logger"):
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_get_span:
                mock_get_span.return_value = INVALID_SPAN

                FastAPIFactoryUtilitiesError(message=message)  # pylint: disable=pointless-exception-statement

                # Should not raise any errors and should not call span methods

    def test_otel_span_attribute_conversion(self) -> None:
        """Test OpenTelemetry span attribute value conversion for different types."""
        message = "Test error message"
        mock_span = Mock()
        mock_span.is_recording.return_value = True

        with patch("fastapi_factory_utilities.core.exceptions._logger"):
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_get_span:
                mock_get_span.return_value = mock_span

                # Test with various attribute types
                FastAPIFactoryUtilitiesError(  # pylint: disable=pointless-exception-statement
                    message=message,
                    **{  # type: ignore[arg-type]
                        "str_attr": "string_value",
                        "int_attr": 42,
                        "float_attr": 3.14,
                        "bool_attr": True,
                        "list_attr": [1, 2, 3],
                        "tuple_attr": (1, 2, 3),
                        "complex_attr": complex(1, 2),  # Should be converted to string
                    },
                )

                # Check that all attributes were set
                expected_calls = [
                    ("str_attr", "string_value"),
                    ("int_attr", 42),
                    ("float_attr", 3.14),
                    ("bool_attr", True),
                    ("list_attr", [1, 2, 3]),
                    ("tuple_attr", (1, 2, 3)),
                    ("complex_attr", "(1+2j)"),  # Complex converted to string
                ]

                assert mock_span.set_attribute.call_count == len(expected_calls)
                for expected_call in expected_calls:
                    mock_span.set_attribute.assert_any_call(*expected_call)

    def test_inheritance_from_exception(self) -> None:
        """Test that FastAPIFactoryUtilitiesError properly inherits from Exception."""
        message = "Test error message"

        with patch("fastapi_factory_utilities.core.exceptions._logger"):
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError(message=message)

                assert isinstance(exception, Exception)
                assert str(exception) == message

    def test_exception_with_multiple_args(self) -> None:
        """Test exception initialization with multiple positional arguments."""
        message = "Test error message"
        arg1 = "additional_arg1"
        arg2 = "additional_arg2"

        with patch("fastapi_factory_utilities.core.exceptions._logger") as mock_logger:
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_span:
                mock_span.return_value = INVALID_SPAN

                exception = FastAPIFactoryUtilitiesError(message, arg1, arg2)

                assert exception.message == message
                mock_logger.log.assert_called_once_with(level=logging.ERROR, event=message)
                # Check that all args are preserved in the exception
                assert str(exception) == message

    def test_exception_with_kwargs_preserved_in_span(self) -> None:
        """Test that kwargs are preserved and set as span attributes."""
        message = "Test error message"
        mock_span = Mock()
        mock_span.is_recording.return_value = True

        with patch("fastapi_factory_utilities.core.exceptions._logger"):
            with patch("fastapi_factory_utilities.core.exceptions.get_current_span") as mock_get_span:
                mock_get_span.return_value = mock_span

                FastAPIFactoryUtilitiesError(  # pylint: disable=pointless-exception-statement
                    message=message,
                    **{"user_id": 123, "request_id": "req-456", "error_code": "E001"},  # type: ignore[arg-type]
                )

                # Verify span attributes were set
                expected_attributes = [("user_id", 123), ("request_id", "req-456"), ("error_code", "E001")]

                for attr_name, attr_value in expected_attributes:
                    mock_span.set_attribute.assert_any_call(attr_name, attr_value)
