"""
Crawler API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query, Response
from fastapi.responses import PlainTextResponse, JSONResponse
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import json

from app.models.request import CrawlRequestModel, BatchCrawlRequestModel
from app.models.response import TaskResponseModel, TaskStatus, ErrorResponse
from app.services.crawler_service import CrawlerService, get_crawler_service
from app.api.auth import verify_api_key

router = APIRouter()


@router.post("/", response_model=TaskResponseModel, summary="Create crawl task")
async def create_crawl_task(
    request: CrawlRequestModel,
    background_tasks: BackgroundTasks,
    crawler_service: CrawlerService = Depends(get_crawler_service),
    api_key_info: Optional[Dict] = Depends(verify_api_key)
):
    """
    Create a new crawl task for a single URL.
    
    - **url**: The URL to crawl
    - **config**: Crawl configuration options
    - **options**: Additional options
    
    Returns a task ID that can be used to track progress.
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Create task response
        task_response = TaskResponseModel(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            config=request.config.dict()
        )
        
        # Store task in service
        await crawler_service.create_task(task_id, request, task_response)
        
        # Start crawling in background
        background_tasks.add_task(
            crawler_service.execute_crawl_task,
            task_id,
            request
        )
        
        return task_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create crawl task: {str(e)}"
        )


@router.post("/crawl/batch", response_model=Dict[str, Any])
async def create_batch_crawl_task(
    request: BatchCrawlRequestModel,
    background_tasks: BackgroundTasks,
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """
    Create a batch crawl task for multiple URLs.
    
    - **urls**: List of URLs to crawl
    - **config**: Crawl configuration applied to all URLs
    - **options**: Additional options
    
    Returns a batch ID and individual task IDs.
    """
    try:
        batch_id = str(uuid.uuid4())
        task_ids = []
        
        # Create individual tasks for each URL
        for url in request.urls:
            task_id = str(uuid.uuid4())
            task_ids.append(task_id)
            
            # Create individual request
            individual_request = CrawlRequestModel(
                url=url,
                config=request.config,
                options=request.options
            )
            
            # Create task response
            task_response = TaskResponseModel(
                task_id=task_id,
                status=TaskStatus.PENDING,
                progress=0.0,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                config=request.config.dict()
            )
            
            # Store task
            await crawler_service.create_task(task_id, individual_request, task_response)
            
            # Start crawling in background
            background_tasks.add_task(
                crawler_service.execute_crawl_task,
                task_id,
                individual_request
            )
        
        return {
            "batch_id": batch_id,
            "task_ids": task_ids,
            "total_tasks": len(task_ids),
            "status": "created"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create batch crawl task: {str(e)}"
        )


@router.get("/crawl/{task_id}", response_model=TaskResponseModel)
async def get_task_status(
    task_id: str,
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """
    Get the status of a crawl task.
    
    - **task_id**: The task ID returned from the crawl endpoint
    
    Returns the current status, progress, and results (if completed).
    """
    try:
        task = await crawler_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.get("/crawl/{task_id}/result")
async def get_task_result(
    task_id: str,
    format: str = "json",
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """
    Get the result of a completed crawl task.
    
    - **task_id**: The task ID
    - **format**: Result format (json, markdown, html, text)
    
    Returns the crawl result in the specified format.
    """
    try:
        task = await crawler_service.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} is not completed yet"
            )
        
        if not task.result:
            raise HTTPException(
                status_code=404,
                detail=f"No result available for task {task_id}"
            )
        
        # Return result in requested format
        if format == "markdown":
            return {"content": task.result.markdown, "format": "markdown"}
        elif format == "html":
            return {"content": task.result.html, "format": "html"}
        elif format == "text":
            return {"content": task.result.text, "format": "text"}
        else:  # json
            return task.result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task result: {str(e)}"
        )


@router.delete("/crawl/{task_id}")
async def cancel_task(
    task_id: str,
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """
    Cancel a running crawl task.
    
    - **task_id**: The task ID to cancel
    
    Returns confirmation of cancellation.
    """
    try:
        success = await crawler_service.cancel_task(task_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found or cannot be cancelled"
            )
        
        return {"message": f"Task {task_id} cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.get("/")
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    crawler_service: CrawlerService = Depends(get_crawler_service),
    api_key_info: Optional[Dict] = Depends(verify_api_key)
):
    """
    List crawl tasks with optional filtering.

    - **status**: Filter by task status (pending, running, completed, failed)
    - **limit**: Maximum number of tasks to return (1-1000)
    - **offset**: Number of tasks to skip for pagination

    Returns a paginated list of tasks.
    """
    try:
        tasks = await crawler_service.list_tasks(
            status=status,
            limit=limit,
            offset=offset
        )

        return {
            "tasks": tasks,
            "total": len(tasks),
            "limit": limit,
            "offset": offset,
            "has_more": len(tasks) == limit
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.get("/stats", summary="Get crawling statistics")
async def get_crawl_stats(
    crawler_service: CrawlerService = Depends(get_crawler_service),
    api_key_info: Optional[Dict] = Depends(verify_api_key)
):
    """
    Get comprehensive crawling statistics.

    Returns:
        dict: Statistics about crawling tasks and performance
    """
    try:
        all_tasks = await crawler_service.list_tasks()

        stats = {
            "total_tasks": len(all_tasks),
            "status_breakdown": {},
            "success_rate": 0.0,
            "average_crawl_time": 0.0,
            "total_pages_crawled": len(all_tasks),
            "last_24h_tasks": 0
        }

        # Calculate status breakdown
        for task in all_tasks:
            status = task.status.value if hasattr(task.status, 'value') else str(task.status)
            stats["status_breakdown"][status] = stats["status_breakdown"].get(status, 0) + 1

        # Calculate success rate
        completed = stats["status_breakdown"].get("completed", 0)
        failed = stats["status_breakdown"].get("failed", 0)
        total_finished = completed + failed
        if total_finished > 0:
            stats["success_rate"] = (completed / total_finished) * 100

        # Calculate average crawl time
        crawl_times = [task.result.crawl_time for task in all_tasks
                      if task.result and hasattr(task.result, 'crawl_time')]
        if crawl_times:
            stats["average_crawl_time"] = sum(crawl_times) / len(crawl_times)

        # Count last 24h tasks
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        stats["last_24h_tasks"] = len([
            task for task in all_tasks
            if task.created_at and task.created_at > yesterday
        ])

        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.post("/validate", summary="Validate crawl request")
async def validate_crawl_request(
    request: CrawlRequestModel,
    api_key_info: Optional[Dict] = Depends(verify_api_key)
):
    """
    Validate a crawl request without executing it.

    Args:
        request: The crawl request to validate

    Returns:
        dict: Validation result
    """
    try:
        # Basic URL validation
        from urllib.parse import urlparse
        parsed = urlparse(request.url)

        if not parsed.scheme or not parsed.netloc:
            return {
                "valid": False,
                "errors": ["Invalid URL format"],
                "warnings": []
            }

        warnings = []
        errors = []

        # Check URL scheme
        if parsed.scheme not in ['http', 'https']:
            errors.append(f"Unsupported URL scheme: {parsed.scheme}")

        # Check for common issues
        if len(request.url) > 2048:
            warnings.append("URL is very long, may cause issues")

        # Validate configuration
        if request.config.word_count_threshold < 0:
            errors.append("Word count threshold cannot be negative")

        if request.config.word_count_threshold > 10000:
            warnings.append("Very high word count threshold may filter out most content")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "url_info": {
                "scheme": parsed.scheme,
                "domain": parsed.netloc,
                "path": parsed.path
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate request: {str(e)}"
        )


@router.get("/{task_id}/download", summary="Download task result")
async def download_task_result(
    task_id: str,
    format: str = Query("json", regex="^(json|markdown|html|text)$"),
    crawler_service: CrawlerService = Depends(get_crawler_service),
    api_key_info: Optional[Dict] = Depends(verify_api_key)
):
    """
    Download the result of a completed crawl task as a file.

    Args:
        task_id: The task ID
        format: File format (json, markdown, html, text)

    Returns:
        File download response
    """
    try:
        task = await crawler_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=f"Task {task_id} is not completed yet")

        if not task.result:
            raise HTTPException(status_code=404, detail=f"No result available for task {task_id}")

        # Prepare content and filename
        if format == "markdown":
            content = task.result.markdown or ""
            filename = f"crawl_result_{task_id}.md"
            media_type = "text/markdown"
        elif format == "html":
            content = task.result.html or ""
            filename = f"crawl_result_{task_id}.html"
            media_type = "text/html"
        elif format == "text":
            content = task.result.text or ""
            filename = f"crawl_result_{task_id}.txt"
            media_type = "text/plain"
        else:  # json
            content = json.dumps(task.result.dict(), indent=2, default=str)
            filename = f"crawl_result_{task_id}.json"
            media_type = "application/json"

        # Return file response
        return Response(
            content=content.encode('utf-8'),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(content.encode('utf-8')))
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download result: {str(e)}"
        )


@router.post("/quick", summary="Quick crawl (synchronous)")
async def quick_crawl(
    request: CrawlRequestModel,
    timeout: int = Query(30, ge=5, le=300, description="Timeout in seconds"),
    crawler_service: CrawlerService = Depends(get_crawler_service),
    api_key_info: Optional[Dict] = Depends(verify_api_key)
):
    """
    Perform a quick synchronous crawl with timeout.

    Args:
        request: The crawl request
        timeout: Maximum time to wait for completion (5-300 seconds)

    Returns:
        dict: Crawl result or timeout error
    """
    try:
        import asyncio

        # Create task
        task_id = str(uuid.uuid4())
        task_response = TaskResponseModel(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            config=request.config.dict()
        )

        await crawler_service.create_task(task_id, request, task_response)

        # Execute crawl with timeout
        try:
            await asyncio.wait_for(
                crawler_service.execute_crawl_task(task_id, request),
                timeout=timeout
            )

            # Get result
            final_task = await crawler_service.get_task(task_id)
            if final_task and final_task.status == TaskStatus.COMPLETED:
                return {
                    "success": True,
                    "task_id": task_id,
                    "result": final_task.result.dict() if final_task.result else None,
                    "crawl_time": final_task.result.crawl_time if final_task.result else None
                }
            else:
                return {
                    "success": False,
                    "task_id": task_id,
                    "error": final_task.error if final_task else "Unknown error",
                    "status": final_task.status.value if final_task else "unknown"
                }

        except asyncio.TimeoutError:
            # Cancel the task
            await crawler_service.cancel_task(task_id)
            raise HTTPException(
                status_code=408,
                detail=f"Crawl timed out after {timeout} seconds"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform quick crawl: {str(e)}"
        )
