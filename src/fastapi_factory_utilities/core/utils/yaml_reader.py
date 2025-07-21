"""Provides a class for reading YAML files and converting them to Pydantic models."""

# mypy: disable-error-code="unused-ignore"

import os
import re
from pathlib import Path
from typing import Any, cast

from structlog.stdlib import BoundLogger, get_logger
from yaml import SafeLoader

logger: BoundLogger = get_logger()


class UnableToReadYamlFileError(Exception):
    """Raised when there is an error reading a YAML file."""

    def __init__(self, file_path: Path | None = None, message: str = "") -> None:
        """Initializes the exception.

        Args:
          file_path (str): The path to the YAML file.
          message (str): The error message.
        """
        super().__init__(f"Error reading YAML file: {file_path} - {message}")


class YamlFileReader:
    """Handles reading YAML files and converting them to Pydantic models."""

    re_pattern: re.Pattern[str] = re.compile(r"\${([A-Za-z0-9\-\_]+):?([A-Za-z0-9\-\_\/\:\.]*)?}")

    def __init__(
        self,
        file_path: Path,
        yaml_base_key: str | None = None,
        use_environment_injection: bool = True,
    ) -> None:
        """Initializes the YAML file reader.

        Args:
          file_path (str): The path to the YAML file.
          yaml_base_key (str | None, optional): The base key
          in the YAML file to read from. Defaults to None.
          use_environment_injection (bool, optional): Whether to use
          environment injection. Defaults to True.
        """
        # Store the file path and base key for YAML reading
        self._yaml_base_key: str | None = yaml_base_key
        self._file_path: Path = file_path

        # Store whether to use environment injection
        self._use_environment_injection: bool = use_environment_injection

    def _filter_data_with_base_key(self, yaml_data: dict[str, Any]) -> dict[str, Any] | None:
        """Extracts the data from the YAML file with the base key.

        Args:
            yaml_data (dict): The data from the YAML file.

        Returns:
            dict: The filtered data from the YAML file.

        Raises:
            KeyError: If the base key is not found in the YAML file.
        """
        if self._yaml_base_key is not None:
            keys: list[str] = self._yaml_base_key.split(".")
            while len(keys) != 0:
                key: str = keys.pop(0)
                try:
                    yaml_data = yaml_data[key]
                except KeyError:
                    logger.warning(f"Base key {key} not found in YAML file" + " from {self._yaml_base_key}")
                    return dict()
        return yaml_data

    def _read_yaml_file(self, file_path: Path) -> dict[str, Any]:
        """Reads the YAML file and returns the data as a dictionary.

        Args:
            file_path (Path): The path to the YAML file.

        Returns:
            dict: The data from the YAML file.

        Raises:
            ValueError: If there is an error reading the file.
            FileNotFoundError: If the file is not found.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file=file_path, encoding="UTF-8") as file:
            loader = SafeLoader(file)

            try:
                yaml_data: dict[str, Any] = cast(
                    dict[str, Any],
                    loader.get_data(),  # type: ignore
                )
            except Exception as exception:
                raise ValueError(f"Error reading YAML file: {file_path}") from exception

            return yaml_data

    def _inject_environment_variables(
        self, yaml_data: dict[str, Any] | str | list[str] | bool | int
    ) -> dict[str, Any] | str | list[str] | bool | int:
        """Injects environment variables into the YAML data recursively.

        Args:
            yaml_data (dict | str | list | bool): The data from the YAML file.

        Returns:
            dict: The data from the YAML file
            with environment variables injected.

        Raises:
            ValueError: If the YAML data is None.
        """
        if isinstance(yaml_data, dict):
            for key, value in yaml_data.items():
                yaml_data[key] = self._inject_environment_variables(value)
        elif isinstance(yaml_data, list):
            yaml_data = [cast(str, self._inject_environment_variables(yaml_data=value)) for value in yaml_data]
        elif isinstance(yaml_data, bool) or isinstance(yaml_data, int):
            return yaml_data
        elif isinstance(yaml_data, str):  # type: ignore
            while True:
                match = self.re_pattern.search(yaml_data)
                if match is None:
                    break
                env_key = match.group(1)
                env_default = match.group(2)
                env_value = os.getenv(env_key, env_default)
                yaml_data = yaml_data.replace(match.group(0), env_value)
        else:
            raise ValueError(f"Type not supported: {type(yaml_data)}")
        return yaml_data

    def read(self) -> dict[str, Any]:
        """Reads the YAML file and converts it to a Pydantic model with env injected.

        Raises:
            UnableToReadYamlFileError: If there is an error reading the file.
        """
        # Read the YAML file and filter the data with the base key
        try:
            yaml_data: dict[str, Any] | None = self._filter_data_with_base_key(
                self._read_yaml_file(file_path=self._file_path)
            )
        except (FileNotFoundError, ValueError, KeyError) as exception:
            raise UnableToReadYamlFileError(file_path=self._file_path, message=str(exception)) from exception

        if yaml_data is None:
            return dict()

        if self._use_environment_injection:
            yaml_data_with_env_injected: dict[str, Any] = cast(
                dict[str, Any], self._inject_environment_variables(yaml_data)
            )
            return dict[str, Any](yaml_data_with_env_injected)
        else:
            return dict[str, Any](yaml_data)
