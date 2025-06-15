"""
Crawl4AI Web Application - Main FastAPI Application
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings, STATIC_DIR, TEMPLATES_DIR, API_V1_PREFIX
from app.api import crawler, websocket, config as config_api
from app.models.response import HealthCheckResponse
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📡 Server will be available at http://{settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Crawl4AI Web Application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Configure templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Include API routers
app.include_router(
    crawler.router,
    prefix=API_V1_PREFIX,
    tags=["crawler"]
)

app.include_router(
    config_api.router,
    prefix=API_V1_PREFIX,
    tags=["config"]
)

# Include WebSocket router
app.include_router(
    websocket.router,
    tags=["websocket"]
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "api_prefix": API_V1_PREFIX,
        }
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(),
        services={
            "crawl4ai": "available",
            "fastapi": "running"
        },
        metrics={
            "max_concurrent_tasks": settings.max_concurrent_tasks,
            "max_memory_usage": settings.max_memory_usage,
        }
    )


@app.get("/playground", response_class=HTMLResponse)
async def playground(request: Request):
    """Serve the API playground page."""
    if not settings.enable_playground:
        return HTMLResponse("Playground is disabled", status_code=404)
    
    return templates.TemplateResponse(
        "playground.html",
        {
            "request": request,
            "app_name": settings.app_name,
            "api_prefix": API_V1_PREFIX,
        }
    )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_code": 404,
            "error_message": "Page not found",
        },
        status_code=404
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error_code": 500,
            "error_message": "Internal server error",
        },
        status_code=500
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
