"""Python exceptions for the Hydra service."""

from fastapi_factory_utilities.core.exceptions import FastAPIFactoryUtilitiesError


class HydraError(FastAPIFactoryUtilitiesError):
    """Base class for all exceptions raised by the Hydra service."""


class HydraOperationError(HydraError):
    """Exception raised when a Hydra operation fails."""


class HydraTokenInvalidError(HydraError):
    """Exception raised when a Hydra token is invalid."""
