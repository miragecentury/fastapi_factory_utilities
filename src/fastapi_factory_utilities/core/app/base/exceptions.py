"""Provides the exceptions for the application factory."""


class BaseApplicationException(BaseException):
    """Base application exception."""

    pass


class ApplicationFactoryException(BaseApplicationException):
    """Application factory exception."""

    pass


class ApplicationConfigFactoryException(BaseApplicationException):
    """Application configuration factory exception."""

    pass


class ApplicationPluginManagerException(BaseApplicationException):
    """Application plugin manager exception."""

    pass
