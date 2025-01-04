"""Testing the importlib module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from fastapi_factory_utilities.core.utils.importlib import get_path_file_in_package


def test_get_path_file_in_package_file_found() -> None:
    """Test the case where the file is found."""
    # Mock the files function from importlib.resources
    with patch("fastapi_factory_utilities.core.utils.importlib.files") as files_mock:
        # Mock the joinpath method of the files object
        joinpath_mock = files_mock.return_value.joinpath
        joinpath_mock.return_value = Path("/path/to/file.txt")

        # Call the function
        result = get_path_file_in_package(filename="file.txt", package="package")

        # Assert that the joinpath method was called with the correct arguments
        joinpath_mock.assert_called_once_with("file.txt")

        # Assert that the result is the expected path
        assert result == Path("/path/to/file.txt")


def test_get_path_file_in_package_file_not_found() -> None:
    """Test the case where the file is not found."""
    # Mock the files function from importlib.resources
    with patch("fastapi_factory_utilities.core.utils.importlib.files") as files_mock:
        # Mock the joinpath method of the files object to raise FileNotFoundError
        joinpath_mock = files_mock.return_value.joinpath
        joinpath_mock.side_effect = FileNotFoundError

        # Call the function and assert that it raises FileNotFoundError
        with pytest.raises(FileNotFoundError):
            get_path_file_in_package("file.txt", "package")


def test_get_path_file_in_package_package_not_found() -> None:
    """Test the case where the package is not found."""
    # Mock the files function from importlib.resources to raise ImportError
    with patch("fastapi_factory_utilities.core.utils.importlib.files", side_effect=ImportError):
        # Call the function and assert that it raises ImportError
        with pytest.raises(ImportError):
            get_path_file_in_package("file.txt", "package")
