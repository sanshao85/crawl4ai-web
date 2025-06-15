"""
Data models for Crawl4AI Web Application
"""

from .request import CrawlRequestModel, CrawlConfigModel, BatchCrawlRequestModel
from .response import TaskResponseModel, CrawlResultModel, ErrorResponse, TaskStatus

__all__ = [
    "CrawlRequestModel",
    "CrawlConfigModel", 
    "BatchCrawlRequestModel",
    "TaskResponseModel",
    "CrawlResultModel",
    "ErrorResponse",
    "TaskStatus",
]
