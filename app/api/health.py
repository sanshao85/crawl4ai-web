"""
Health check and system status API endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
import psutil
import platform
import sys
from app.services.crawler_service import CrawlerService, get_crawler_service

router = APIRouter()


@router.get("/", summary="Basic health check")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        dict: Basic health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Crawl4AI Web Application",
        "version": "1.0.0"
    }


@router.get("/detailed", summary="Detailed system health")
async def detailed_health_check(
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """
    Detailed health check with system information.
    
    Returns:
        dict: Comprehensive health and system status
    """
    try:
        # System information
        system_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
        }
        
        # Service status
        service_status = {
            "crawler_service": "available",
            "active_tasks": len(await crawler_service.list_tasks(status="running")),
            "total_tasks": len(await crawler_service.list_tasks())
        }
        
        # Check Crawl4AI availability
        crawl4ai_status = "available"
        try:
            import crawl4ai
            crawl4ai_status = "available"
        except ImportError:
            crawl4ai_status = "unavailable"
        
        # Check Playwright availability
        playwright_status = "available"
        try:
            import playwright
            playwright_status = "available"
        except ImportError:
            playwright_status = "unavailable"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Crawl4AI Web Application",
            "version": "1.0.0",
            "system": system_info,
            "services": service_status,
            "dependencies": {
                "crawl4ai": crawl4ai_status,
                "playwright": playwright_status
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/metrics", summary="System metrics")
async def get_metrics():
    """
    Get system performance metrics.
    
    Returns:
        dict: System performance metrics
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/') if platform.system() != 'Windows' else psutil.disk_usage('C:')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
