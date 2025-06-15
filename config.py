"""
Crawl4AI Web Application Configuration
"""
import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    reload: bool = False
    
    # Application Settings
    app_name: str = "Crawl4AI Web Application"
    app_version: str = "1.0.0"
    app_description: str = "Web interface for Crawl4AI crawler"
    
    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    cors_origins: List[str] = ["http://localhost:8080", "http://127.0.0.1:8080"]
    
    # Crawl4AI Settings
    max_concurrent_tasks: int = 10
    max_task_duration: int = 300  # 5 minutes
    max_memory_usage: int = 512 * 1024 * 1024  # 512MB
    max_response_size: int = 50 * 1024 * 1024  # 50MB
    
    # Rate Limiting
    rate_limit_per_minute: int = 10
    rate_limit_per_hour: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Cache Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_expire_time: int = 3600  # 1 hour
    
    # Development Settings
    enable_docs: bool = True
    enable_playground: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Static file configuration
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

# API configuration
API_V1_PREFIX = "/api/v1"
WEBSOCKET_ENDPOINT = "/ws"

# Default Crawl4AI configuration
DEFAULT_CRAWL_CONFIG = {
    "word_count_threshold": 200,
    "extraction_strategy": "default",
    "css_selector": None,
    "wait_for": None,
    "screenshot": False,
    "pdf": False,
    "remove_overlay_elements": True,
    "exclude_external_links": True,
    "exclude_social_media_links": True,
}

# Supported extraction strategies
EXTRACTION_STRATEGIES = [
    {"value": "default", "label": "Default", "description": "Standard content extraction"},
    {"value": "llm", "label": "LLM", "description": "AI-powered extraction"},
    {"value": "css", "label": "CSS Selector", "description": "CSS selector-based extraction"},
    {"value": "regex", "label": "Regex", "description": "Regular expression extraction"},
]

# Supported output formats
OUTPUT_FORMATS = [
    {"value": "markdown", "label": "Markdown", "extension": "md"},
    {"value": "html", "label": "HTML", "extension": "html"},
    {"value": "json", "label": "JSON", "extension": "json"},
    {"value": "text", "label": "Plain Text", "extension": "txt"},
]
