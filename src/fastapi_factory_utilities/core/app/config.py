"""Provide the configuration for the app server."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from fastapi_factory_utilities.core.app.base.exceptions import (
    ApplicationConfigFactoryException,
)
from fastapi_factory_utilities.core.utils.configs import (
    UnableToReadConfigFileError,
    ValueErrorConfigError,
    build_config_from_file_in_package,
)
from fastapi_factory_utilities.core.utils.log import LoggingConfig

from .enums import EnvironmentEnum


def default_allow_all() -> list[str]:
    """Default allow all."""
    return ["*"]


class CorsConfig(BaseModel):
    """CORS configuration."""

    allow_origins: list[str] = Field(default_factory=default_allow_all, description="Allowed origins")
    allow_credentials: bool = Field(default=True, description="Allow credentials")
    allow_methods: list[str] = Field(default_factory=default_allow_all, description="Allowed methods")
    allow_headers: list[str] = Field(default_factory=default_allow_all, description="Allowed headers")
    expose_headers: list[str] = Field(default_factory=list, description="Exposed headers")
    max_age: int = Field(default=600, description="Max age")


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    workers: int = Field(default=1, description="Number of workers")


class DevelopmentConfig(BaseModel):
    """Development configuration."""

    debug: bool = Field(default=False, description="Debug mode")
    reload: bool = Field(default=False, description="Reload mode")


class BaseApplicationConfig(BaseModel):
    """Application configuration abstract class."""

    # Application configuration
    # (mainly used for monitoring and information reporting)
    service_namespace: str = Field(description="Service namespace")
    environment: EnvironmentEnum = Field(description="Deployed environment")
    service_name: str = Field(description="Service name")
    description: str = Field(description="Service description")
    version: str = Field(description="Service version")

    root_path: str = Field(default="", description="Root path")


class RootConfig(BaseModel):
    """Root configuration."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")

    application: BaseApplicationConfig = Field(description="Application configuration")
    server: ServerConfig = Field(description="Server configuration", default_factory=ServerConfig)
    cors: CorsConfig = Field(description="CORS configuration", default_factory=CorsConfig)
    development: DevelopmentConfig = Field(description="Development configuration", default_factory=DevelopmentConfig)
    logging: list[LoggingConfig] = Field(description="Logging configuration", default_factory=list)


class RootConfigBuilder:
    """Application configuration builder."""

    DEFAULT_FILENAME: str = "application.yaml"
    DEFAULT_YAML_BASE_KEY: str | None = None

    def __init__(
        self,
        package_name: str,
        config_class: type[RootConfig],
        filename: str = DEFAULT_FILENAME,
        yaml_base_key: str | None = DEFAULT_YAML_BASE_KEY,
    ) -> None:
        """Instantiate the builder.

        Args:
            package_name (str): The package name.
            config_class (Type[AppConfigAbstract]): The configuration class.
            filename (str, optional): The filename. Defaults to DEFAULT_FILENAME.
            yaml_base_key (str, optional): The YAML base key. Defaults to DEFAULT_YAML_BASE_KEY.
        """
        self.package_name: str = package_name
        self.config_class: type[RootConfig] = config_class
        self.filename: str = filename
        self.yaml_base_key: str | None = yaml_base_key

    def build(self) -> RootConfig:
        """Build the configuration.

        Returns:
            RootConfig: The configuration.
        """
        try:
            config: RootConfig = build_config_from_file_in_package(
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
