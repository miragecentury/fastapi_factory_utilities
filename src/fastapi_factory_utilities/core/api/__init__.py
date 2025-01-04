"""Define the API for the Python Factory."""

from fastapi import APIRouter

from .tags import TagEnum
from .v1.sys import api_v1_sys

api: APIRouter = APIRouter(prefix="/api")

### API v1 ###
# Prefix the API with /api/v1
api_v1: APIRouter = APIRouter(prefix="/v1")
api_v1.include_router(router=api_v1_sys)


### API v2 ###
# Prefix the API with /api/v2
api_v2: APIRouter = APIRouter(prefix="/v2")


### Include the API routers ###
api.include_router(router=api_v1)
api.include_router(router=api_v2)

__all__: list[str] = ["api", "TagEnum"]
