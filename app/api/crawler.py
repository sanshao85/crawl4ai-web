"""
Crawler API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any
import uuid
from datetime import datetime

from app.models.request import CrawlRequestModel, BatchCrawlRequestModel
from app.models.response import TaskResponseModel, TaskStatus, ErrorResponse
from app.services.crawler_service import CrawlerService, get_crawler_service

router = APIRouter()


@router.post("/crawl", response_model=TaskResponseModel)
async def create_crawl_task(
    request: CrawlRequestModel,
    background_tasks: BackgroundTasks,
    crawler_service: CrawlerService = Depends(get_crawler_service)
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


@router.get("/crawl")
async def list_tasks(
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """
    List crawl tasks with optional filtering.
    
    - **status**: Filter by task status (optional)
    - **limit**: Maximum number of tasks to return
    - **offset**: Number of tasks to skip
    
    Returns a list of tasks.
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
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tasks: {str(e)}"
        )
