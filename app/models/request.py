"""
Request models for Crawl4AI Web Application
"""

from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum


class ExtractionType(str, Enum):
    """Supported extraction strategies."""
    DEFAULT = "default"
    LLM = "llm"
    CSS = "css"
    REGEX = "regex"


class CrawlConfigModel(BaseModel):
    """Configuration model for crawl requests."""
    
    # Content processing
    word_count_threshold: int = Field(
        default=200, 
        ge=1, 
        le=10000,
        description="Minimum word count threshold for content"
    )
    extraction_strategy: ExtractionType = Field(
        default=ExtractionType.DEFAULT,
        description="Strategy to use for content extraction"
    )
    
    # Selectors and targeting
    css_selector: Optional[str] = Field(
        default=None,
        description="CSS selector to target specific elements"
    )
    wait_for: Optional[str] = Field(
        default=None,
        description="CSS selector or time to wait for before extraction"
    )
    
    # Output options
    screenshot: bool = Field(
        default=False,
        description="Whether to take a screenshot"
    )
    pdf: bool = Field(
        default=False,
        description="Whether to generate PDF"
    )
    
    # Content filtering
    remove_overlay_elements: bool = Field(
        default=True,
        description="Remove overlay elements like popups"
    )
    exclude_external_links: bool = Field(
        default=True,
        description="Exclude external links from content"
    )
    exclude_social_media_links: bool = Field(
        default=True,
        description="Exclude social media links"
    )
    
    # Advanced options
    user_agent: Optional[str] = Field(
        default=None,
        description="Custom user agent string"
    )
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom HTTP headers"
    )
    timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Request timeout in seconds"
    )
    
    @validator('css_selector')
    def validate_css_selector(cls, v):
        """Validate CSS selector format."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v
    
    @validator('headers')
    def validate_headers(cls, v):
        """Validate HTTP headers."""
        if not isinstance(v, dict):
            raise ValueError("Headers must be a dictionary")
        return v


class CrawlRequestModel(BaseModel):
    """Model for single URL crawl requests."""
    
    url: HttpUrl = Field(
        description="URL to crawl"
    )
    config: CrawlConfigModel = Field(
        default_factory=CrawlConfigModel,
        description="Crawl configuration"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional options"
    )
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format and security."""
        url_str = str(v)
        
        # Check protocol
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError("URL must use HTTP or HTTPS protocol")
        
        # Check for localhost/internal IPs (basic security)
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        for blocked in blocked_hosts:
            if blocked in url_str.lower():
                raise ValueError(f"Access to {blocked} is not allowed")
        
        return v


class BatchCrawlRequestModel(BaseModel):
    """Model for batch crawl requests."""
    
    urls: List[HttpUrl] = Field(
        min_items=1,
        max_items=10,
        description="List of URLs to crawl"
    )
    config: CrawlConfigModel = Field(
        default_factory=CrawlConfigModel,
        description="Crawl configuration applied to all URLs"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional options"
    )
    
    @validator('urls')
    def validate_urls(cls, v):
        """Validate all URLs in the batch."""
        if len(v) > 10:
            raise ValueError("Maximum 10 URLs allowed per batch")
        return v


class ConfigValidationRequest(BaseModel):
    """Model for configuration validation requests."""
    
    config: CrawlConfigModel = Field(
        description="Configuration to validate"
    )


class HistoryRequest(BaseModel):
    """Model for history-related requests."""
    
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of history items to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )
    filter_url: Optional[str] = Field(
        default=None,
        description="Filter by URL pattern"
    )
