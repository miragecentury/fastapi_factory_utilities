"""Package for system related API endpoints."""

from fastapi import APIRouter

from .health import api_v1_sys_health
from .readiness import api_v1_sys_readiness

api_v1_sys = APIRouter(prefix="/sys")
api_v1_sys.include_router(router=api_v1_sys_health)
api_v1_sys.include_router(router=api_v1_sys_readiness)

__all__: list[str] = ["api_v1_sys"]
