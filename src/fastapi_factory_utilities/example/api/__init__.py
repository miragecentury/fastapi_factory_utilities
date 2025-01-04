"""Provide the API for the example package."""

from fastapi import APIRouter

from .books import api_v1_books_router, api_v2_books_router

api_router: APIRouter = APIRouter(prefix="/api")

# -- API v1
api_router_v1: APIRouter = APIRouter(prefix="/v1")
api_router_v1.include_router(router=api_v1_books_router)

# -- API v2
api_router_v2: APIRouter = APIRouter(prefix="/v2")
api_router_v2.include_router(router=api_v2_books_router)

# -- Include API versions
api_router.include_router(router=api_router_v1)
api_router.include_router(router=api_router_v2)
