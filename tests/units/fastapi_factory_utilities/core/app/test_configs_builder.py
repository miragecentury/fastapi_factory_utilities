"""Provides unit tests for the RootConfigBuilder module."""

from unittest.mock import patch

import pytest

from fastapi_factory_utilities.core.app.config import RootConfig, RootConfigBuilder
from fastapi_factory_utilities.core.app.exceptions import (
    ApplicationConfigFactoryException,
)
from fastapi_factory_utilities.core.utils.configs import (
    UnableToReadConfigFileError,
    ValueErrorConfigError,
)


class TestRootConfigBuilder:
    """Test suite for the RootConfigBuilder class."""

    @pytest.mark.parametrize(
        "exception_raise,expected_exception",
        [
            pytest.param(Exception, ApplicationConfigFactoryException, id="Exception"),
            pytest.param(
                UnableToReadConfigFileError, ApplicationConfigFactoryException, id="UnableToReadConfigFileError"
            ),
            pytest.param(ValueErrorConfigError, ApplicationConfigFactoryException, id="ValueErrorConfigError"),
        ],
    )
    def test_root_config_exception_handling(
        self, exception_raise: type[Exception], expected_exception: type[Exception]
    ) -> None:
        """Test that the RootConfigBuilder handles exceptions."""
        with patch(
            "fastapi_factory_utilities.core.utils.configs.build_config_from_file_in_package"
        ) as mock_build_config_from_file_in_package:
            mock_build_config_from_file_in_package.side_effect = exception_raise
            with pytest.raises(expected_exception):
                RootConfigBuilder(
                    package_name="tests",
                    config_class=RootConfig,
                    filename="application.yaml",
                    yaml_base_key=None,
                ).build()
