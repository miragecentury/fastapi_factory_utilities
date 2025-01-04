"""Provide the configuration for the app server."""

from pydantic import Field

from fastapi_factory_utilities.core.app.base.exceptions import (
    ApplicationConfigFactoryException,
)
from fastapi_factory_utilities.core.app.base.plugins_manager_abstract import (
    PluginsActivationList,
)
from fastapi_factory_utilities.core.utils.configs import (
    UnableToReadConfigFileError,
    ValueErrorConfigError,
    build_config_from_file_in_package,
)
from fastapi_factory_utilities.core.utils.log import LoggingConfig

from ..enums import EnvironmentEnum
from .fastapi_application_abstract import FastAPIConfigAbstract


class AppConfigAbstract(FastAPIConfigAbstract, PluginsActivationList):
    """Application configuration abstract class."""

    environment: EnvironmentEnum
    service_name: str
    service_namespace: str

    logging: list[LoggingConfig] = Field(default_factory=list, description="Logging configuration.")


class AppConfigBuilder:
    """Application configuration builder."""

    DEFAULT_FILENAME: str = "application.yaml"
    DEFAULT_YAML_BASE_KEY: str = "application"

    def __init__(
        self,
        package_name: str,
        config_class: type[AppConfigAbstract],
        filename: str = DEFAULT_FILENAME,
        yaml_base_key: str = DEFAULT_YAML_BASE_KEY,
    ) -> None:
        """Instantiate the builder.

        Args:
            package_name (str): The package name.
            config_class (Type[AppConfigAbstract]): The configuration class.
            filename (str, optional): The filename. Defaults to DEFAULT_FILENAME.
            yaml_base_key (str, optional): The YAML base key. Defaults to DEFAULT_YAML_BASE_KEY.
        """
        self.package_name: str = package_name
        self.config_class: type[AppConfigAbstract] = config_class
        self.filename: str = filename
        self.yaml_base_key: str = yaml_base_key

    def build(self) -> AppConfigAbstract:
        """Build the configuration.

        Returns:
            AppConfigAbstract: The configuration.
        """
        try:
            config: AppConfigAbstract = build_config_from_file_in_package(
                package_name=self.package_name,
                config_class=self.config_class,
                filename=self.filename,
                yaml_base_key=self.yaml_base_key,
            )
        except UnableToReadConfigFileError as exception:
            raise ApplicationConfigFactoryException("Unable to read the application configuration file.") from exception
        except ValueErrorConfigError as exception:
            raise ApplicationConfigFactoryException(
                "Unable to create the application configuration model."
            ) from exception

        return config
