"""Provide FastAPI dependency for ODM."""

from typing import Any

from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def depends_odm_client(request: Request) -> AsyncIOMotorClient[Any]:
    """Acquire the ODM client from the request.

    Args:
        request (Request): The request.

    Returns:
        AsyncIOMotorClient: The ODM client.
    """
    return request.app.state.odm_client


def depends_odm_database(request: Request) -> AsyncIOMotorDatabase[Any]:
    """Acquire the ODM database from the request.

    Args:
        request (Request): The request.

    Returns:
        AsyncIOMotorClient: The ODM database.
    """
    return request.app.state.odm_database
