"""
Response models for Crawl4AI Web Application
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlResultModel(BaseModel):
    """Model for crawl results."""
    
    url: str = Field(description="The crawled URL")
    title: Optional[str] = Field(default=None, description="Page title")
    
    # Content in different formats
    markdown: Optional[str] = Field(default=None, description="Content in Markdown format")
    html: Optional[str] = Field(default=None, description="Cleaned HTML content")
    text: Optional[str] = Field(default=None, description="Plain text content")
    
    # Extracted data
    extracted_content: Optional[str] = Field(
        default=None, 
        description="Structured extracted content"
    )
    
    # Media content
    screenshot: Optional[str] = Field(
        default=None, 
        description="Base64 encoded screenshot"
    )
    pdf: Optional[str] = Field(
        default=None, 
        description="Base64 encoded PDF"
    )
    
    # Links and media
    links: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Extracted links"
    )
    images: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Extracted images"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    # Performance metrics
    crawl_time: Optional[float] = Field(
        default=None,
        description="Time taken to crawl in seconds"
    )
    content_size: Optional[int] = Field(
        default=None,
        description="Size of content in bytes"
    )


class TaskResponseModel(BaseModel):
    """Model for task status responses."""
    
    task_id: str = Field(description="Unique task identifier")
    status: TaskStatus = Field(description="Current task status")
    progress: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Task progress (0.0 to 1.0)"
    )
    
    # Results
    result: Optional[CrawlResultModel] = Field(
        default=None,
        description="Crawl result (available when completed)"
    )
    
    # Error information
    error: Optional[str] = Field(
        default=None,
        description="Error message if task failed"
    )
    error_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed error information"
    )
    
    # Timestamps
    created_at: datetime = Field(description="Task creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Task completion timestamp"
    )
    
    # Configuration used
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration used for the task"
    )


class BatchTaskResponseModel(BaseModel):
    """Model for batch task responses."""
    
    batch_id: str = Field(description="Unique batch identifier")
    total_tasks: int = Field(description="Total number of tasks in batch")
    completed_tasks: int = Field(description="Number of completed tasks")
    failed_tasks: int = Field(description="Number of failed tasks")
    
    overall_progress: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall batch progress"
    )
    
    tasks: List[TaskResponseModel] = Field(
        description="Individual task responses"
    )
    
    created_at: datetime = Field(description="Batch creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )
    timestamp: datetime = Field(description="Error timestamp")
    request_id: Optional[str] = Field(
        default=None,
        description="Request identifier for tracking"
    )


class ConfigValidationResponse(BaseModel):
    """Model for configuration validation responses."""
    
    valid: bool = Field(description="Whether the configuration is valid")
    errors: List[str] = Field(
        default_factory=list,
        description="List of validation errors"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="List of validation warnings"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Configuration improvement suggestions"
    )


class HistoryItemModel(BaseModel):
    """Model for history items."""
    
    id: str = Field(description="History item ID")
    url: str = Field(description="Crawled URL")
    title: Optional[str] = Field(default=None, description="Page title")
    status: TaskStatus = Field(description="Task status")
    
    created_at: datetime = Field(description="Creation timestamp")
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Completion timestamp"
    )
    
    config: Dict[str, Any] = Field(description="Configuration used")
    result_size: Optional[int] = Field(
        default=None,
        description="Size of result in bytes"
    )


class HistoryResponse(BaseModel):
    """Model for history responses."""
    
    items: List[HistoryItemModel] = Field(description="History items")
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Items per page")
    offset: int = Field(description="Current offset")
    has_more: bool = Field(description="Whether there are more items")


class HealthCheckResponse(BaseModel):
    """Model for health check responses."""
    
    status: str = Field(description="Service status")
    version: str = Field(description="Application version")
    timestamp: datetime = Field(description="Health check timestamp")
    
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Status of dependent services"
    )
    
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Performance metrics"
    )


class WebSocketMessage(BaseModel):
    """Model for WebSocket messages."""
    
    type: str = Field(description="Message type")
    data: Dict[str, Any] = Field(description="Message data")
    timestamp: datetime = Field(description="Message timestamp")
    task_id: Optional[str] = Field(
        default=None,
        description="Associated task ID"
    )
