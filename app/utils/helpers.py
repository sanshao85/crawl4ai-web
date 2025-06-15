"""
Helper utilities
"""

import re
import math
from datetime import datetime, timedelta
from typing import Optional


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2m 30s")
    """
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{minutes}m"
    
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    
    if remaining_minutes > 0:
        return f"{hours}h {remaining_minutes}m"
    else:
        return f"{hours}h"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "untitled"
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = split_filename(filename)
        max_name_length = 255 - len(ext) - 1
        filename = name[:max_name_length] + '.' + ext if ext else name[:255]
    
    # Ensure it's not empty
    if not filename.strip():
        filename = "untitled"
    
    return filename.strip()


def split_filename(filename: str) -> tuple:
    """
    Split filename into name and extension.
    
    Args:
        filename: Full filename
        
    Returns:
        Tuple of (name, extension)
    """
    if '.' in filename:
        parts = filename.rsplit('.', 1)
        return parts[0], parts[1]
    else:
        return filename, ""


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL string
        
    Returns:
        Domain name or None if invalid
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None


def generate_task_id() -> str:
    """
    Generate a unique task ID.
    
    Returns:
        Unique task ID string
    """
    import uuid
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def parse_wait_condition(wait_for: str) -> tuple:
    """
    Parse wait condition string.
    
    Args:
        wait_for: Wait condition (CSS selector or time in seconds)
        
    Returns:
        Tuple of (wait_type, value) where wait_type is 'time' or 'selector'
    """
    if not wait_for:
        return None, None
    
    wait_for = wait_for.strip()
    
    # Check if it's a number (time in seconds)
    try:
        seconds = float(wait_for)
        return 'time', seconds
    except ValueError:
        pass
    
    # Check if it's a time with unit (e.g., "5s", "2000ms")
    time_pattern = r'^(\d+(?:\.\d+)?)(s|ms)$'
    match = re.match(time_pattern, wait_for.lower())
    if match:
        value, unit = match.groups()
        seconds = float(value)
        if unit == 'ms':
            seconds /= 1000
        return 'time', seconds
    
    # Otherwise, treat as CSS selector
    return 'selector', wait_for


def validate_json_string(json_str: str) -> bool:
    """
    Validate if string is valid JSON.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        True if valid JSON
    """
    try:
        import json
        json.loads(json_str)
        return True
    except (ValueError, TypeError):
        return False


def clean_html_content(html: str) -> str:
    """
    Clean HTML content for display.
    
    Args:
        html: HTML content
        
    Returns:
        Cleaned HTML content
    """
    if not html:
        return ""
    
    # Remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Clean up whitespace
    html = re.sub(r'\s+', ' ', html)
    html = html.strip()
    
    return html


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Estimate reading time for text.
    
    Args:
        text: Text content
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = math.ceil(word_count / words_per_minute)
    
    return max(1, reading_time)  # Minimum 1 minute


def create_safe_dict(data: dict, allowed_keys: list) -> dict:
    """
    Create a safe dictionary with only allowed keys.
    
    Args:
        data: Source dictionary
        allowed_keys: List of allowed keys
        
    Returns:
        Filtered dictionary
    """
    return {key: data[key] for key in allowed_keys if key in data}
