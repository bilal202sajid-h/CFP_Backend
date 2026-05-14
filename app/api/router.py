from fastapi import APIRouter

from .endpoints.admin import router as admin_router
from .endpoints.collections import router as collections_router
from .endpoints.health import router as health_router
from .endpoints.products import router as products_router
from .endpoints.categories import router as categories_router
from .endpoints.frontend_config import router as frontend_config_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(admin_router)
api_router.include_router(collections_router)
api_router.include_router(products_router)
api_router.include_router(categories_router)
api_router.include_router(frontend_config_router)