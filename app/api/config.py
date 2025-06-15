"""
Configuration API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from app.models.request import ConfigValidationRequest, CrawlConfigModel
from app.models.response import ConfigValidationResponse
from config import DEFAULT_CRAWL_CONFIG, EXTRACTION_STRATEGIES, OUTPUT_FORMATS

router = APIRouter()


@router.get("/config/defaults")
async def get_default_config() -> Dict[str, Any]:
    """
    Get the default crawl configuration.
    
    Returns the default configuration that will be used if no custom config is provided.
    """
    return {
        "config": DEFAULT_CRAWL_CONFIG,
        "description": "Default configuration for crawl requests"
    }


@router.get("/config/presets")
async def get_config_presets() -> Dict[str, Any]:
    """
    Get predefined configuration presets.
    
    Returns a list of common configuration presets for different use cases.
    """
    presets = {
        "basic": {
            "name": "Basic Crawl",
            "description": "Simple content extraction with default settings",
            "config": {
                "word_count_threshold": 200,
                "extraction_strategy": "default",
                "remove_overlay_elements": True,
                "exclude_external_links": True,
                "exclude_social_media_links": True,
                "timeout": 30
            }
        },
        "detailed": {
            "name": "Detailed Crawl",
            "description": "Comprehensive extraction with screenshots",
            "config": {
                "word_count_threshold": 100,
                "extraction_strategy": "default",
                "screenshot": True,
                "remove_overlay_elements": True,
                "exclude_external_links": False,
                "exclude_social_media_links": False,
                "timeout": 60
            }
        },
        "fast": {
            "name": "Fast Crawl",
            "description": "Quick extraction with minimal processing",
            "config": {
                "word_count_threshold": 500,
                "extraction_strategy": "default",
                "remove_overlay_elements": False,
                "exclude_external_links": True,
                "exclude_social_media_links": True,
                "timeout": 15
            }
        },
        "ai_extraction": {
            "name": "AI-Powered Extraction",
            "description": "Use LLM for intelligent content extraction",
            "config": {
                "word_count_threshold": 100,
                "extraction_strategy": "llm",
                "remove_overlay_elements": True,
                "exclude_external_links": True,
                "exclude_social_media_links": True,
                "timeout": 90
            }
        },
        "css_targeted": {
            "name": "CSS Targeted",
            "description": "Extract specific elements using CSS selectors",
            "config": {
                "word_count_threshold": 50,
                "extraction_strategy": "css",
                "css_selector": "article, .content, main",
                "remove_overlay_elements": True,
                "exclude_external_links": True,
                "exclude_social_media_links": True,
                "timeout": 45
            }
        }
    }
    
    return {
        "presets": presets,
        "total": len(presets)
    }


@router.post("/config/validate", response_model=ConfigValidationResponse)
async def validate_config(request: ConfigValidationRequest):
    """
    Validate a crawl configuration.
    
    - **config**: The configuration to validate
    
    Returns validation results with errors, warnings, and suggestions.
    """
    try:
        config = request.config
        errors = []
        warnings = []
        suggestions = []
        
        # Validate word count threshold
        if config.word_count_threshold < 1:
            errors.append("word_count_threshold must be at least 1")
        elif config.word_count_threshold > 10000:
            errors.append("word_count_threshold cannot exceed 10000")
        elif config.word_count_threshold < 50:
            warnings.append("Very low word_count_threshold may result in noisy content")
        
        # Validate timeout
        if config.timeout < 5:
            errors.append("timeout must be at least 5 seconds")
        elif config.timeout > 300:
            errors.append("timeout cannot exceed 300 seconds")
        elif config.timeout > 120:
            warnings.append("High timeout values may affect performance")
        
        # Validate CSS selector if provided
        if config.css_selector:
            if len(config.css_selector.strip()) == 0:
                warnings.append("Empty CSS selector will be ignored")
            elif config.extraction_strategy != "css":
                suggestions.append("Consider using 'css' extraction strategy with CSS selector")
        
        # Validate extraction strategy
        valid_strategies = [strategy.value for strategy in config.extraction_strategy.__class__]
        if config.extraction_strategy not in valid_strategies:
            errors.append(f"Invalid extraction strategy. Must be one of: {valid_strategies}")
        
        # Performance suggestions
        if config.screenshot and config.pdf:
            suggestions.append("Generating both screenshot and PDF may slow down crawling")
        
        if not config.remove_overlay_elements:
            suggestions.append("Keeping overlay elements may result in unwanted content")
        
        # Security warnings
        if not config.exclude_external_links:
            warnings.append("Including external links may expose sensitive information")
        
        return ConfigValidationResponse(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate configuration: {str(e)}"
        )


@router.get("/config/strategies")
async def get_extraction_strategies() -> Dict[str, Any]:
    """
    Get available extraction strategies.
    
    Returns a list of supported extraction strategies with descriptions.
    """
    return {
        "strategies": EXTRACTION_STRATEGIES,
        "total": len(EXTRACTION_STRATEGIES)
    }


@router.get("/config/formats")
async def get_output_formats() -> Dict[str, Any]:
    """
    Get available output formats.
    
    Returns a list of supported output formats.
    """
    return {
        "formats": OUTPUT_FORMATS,
        "total": len(OUTPUT_FORMATS)
    }


@router.get("/config/schema")
async def get_config_schema() -> Dict[str, Any]:
    """
    Get the JSON schema for crawl configuration.
    
    Returns the complete schema that can be used for form generation or validation.
    """
    try:
        schema = CrawlConfigModel.schema()
        
        # Add additional metadata for UI generation
        schema["ui_metadata"] = {
            "groups": {
                "content": {
                    "title": "Content Processing",
                    "fields": ["word_count_threshold", "extraction_strategy"]
                },
                "targeting": {
                    "title": "Content Targeting",
                    "fields": ["css_selector", "wait_for"]
                },
                "output": {
                    "title": "Output Options",
                    "fields": ["screenshot", "pdf"]
                },
                "filtering": {
                    "title": "Content Filtering",
                    "fields": [
                        "remove_overlay_elements",
                        "exclude_external_links", 
                        "exclude_social_media_links"
                    ]
                },
                "advanced": {
                    "title": "Advanced Options",
                    "fields": ["user_agent", "headers", "timeout"]
                }
            }
        }
        
        return schema
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get configuration schema: {str(e)}"
        )
