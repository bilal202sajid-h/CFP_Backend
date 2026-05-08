from fastapi import APIRouter

from .endpoints.admin import router as admin_router
from .endpoints.collections import router as collections_router
from .endpoints.health import router as health_router
from .endpoints.products import router as products_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(admin_router)
api_router.include_router(collections_router)
api_router.include_router(products_router)