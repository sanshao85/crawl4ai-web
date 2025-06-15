"""
API modules for Crawl4AI Web Application
"""

from fastapi import APIRouter
from .crawler import router as crawler_router
from .config import router as config_router
from .health import router as health_router
from .auth import router as auth_router

# API version
API_VERSION = "v1"

# Create main API router
api_router = APIRouter(prefix=f"/api/{API_VERSION}")

# Include all routers
api_router.include_router(crawler_router, prefix="/crawl", tags=["Crawling"])
api_router.include_router(config_router, prefix="/config", tags=["Configuration"])
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
