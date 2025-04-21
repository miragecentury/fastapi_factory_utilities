"""Python exceptions for the Kratos service."""

from fastapi_factory_utilities.core.exceptions import FastAPIFactoryUtilitiesError


class KratosError(FastAPIFactoryUtilitiesError):
    """Base class for all exceptions raised by the Kratos service."""


class KratosOperationError(KratosError):
    """Exception raised when a Kratos operation fails."""


class KratosSessionInvalidError(KratosOperationError):
    """Exception raised when a Kratos session is invalid."""
