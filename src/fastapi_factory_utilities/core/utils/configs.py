"""Provides utilities to handle configurations."""

from typing import Any, TypeVar

from pydantic import BaseModel

from fastapi_factory_utilities.core.utils.importlib import get_path_file_in_package
from fastapi_factory_utilities.core.utils.yaml_reader import (
    UnableToReadYamlFileError,
    YamlFileReader,
)

GenericConfigBaseModelType = TypeVar("GenericConfigBaseModelType", bound=BaseModel)  # pylint: disable=invalid-name


class ConfigBaseException(BaseException):
    """Base exception for all the configuration exceptions."""

    pass


class UnableToReadConfigFileError(ConfigBaseException):
    """Exception raised when the configuration file cannot be read.

    Mainly used when the file is not found or the file is not a YAML file.
    """

    pass


class ValueErrorConfigError(ConfigBaseException):
    """Exception raised when the configuration object cannot be created.

    Mainly used when validation fails when creating the configuration object.
    """

    pass


def build_config_from_file_in_package(
    package_name: str,
    filename: str,
    config_class: type[GenericConfigBaseModelType],
    yaml_base_key: str | None = None,
) -> GenericConfigBaseModelType:
    """Build a configuration object from a file in a package.

    Args:
        package_name (str): The package name.
        filename (str): The filename.
        config_class (type[GenericConfigBaseModelType]): The configuration class.
        yaml_base_key (str): The base key in the YAML file.

    Returns:
        GenericConfigBaseModelType: The configuration object.

    Raises:
        UnableToReadConfigFileError: If the configuration file cannot be read.
        ValueErrorConfigError: If the configuration file is invalid.
    """
    # Read the application configuration file
    try:
        yaml_file_content: dict[str, Any] = YamlFileReader(
            file_path=get_path_file_in_package(
                filename=filename,
                package=package_name,
            ),
            yaml_base_key=yaml_base_key,
            use_environment_injection=True,
        ).read()
    except (FileNotFoundError, ImportError, UnableToReadYamlFileError) as exception:
        raise UnableToReadConfigFileError("Unable to read the application configuration file.") from exception

    # Create the application configuration model
    try:
        config: GenericConfigBaseModelType = config_class(**yaml_file_content)
    except ValueError as exception:
        raise ValueErrorConfigError("Unable to create the configuration model.") from exception

    return config
