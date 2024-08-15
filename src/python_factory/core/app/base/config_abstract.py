"""
Provide the configuration for the app server.
"""

from ..enums import EnvironmentEnum
from .fastapi_application_abstract import FastAPIConfigAbstract


class AppConfigAbstract(FastAPIConfigAbstract):
    environment: EnvironmentEnum
    service_name: str
    service_namespace: str