"""
Validation utilities
"""

import re
from urllib.parse import urlparse
from typing import List, Tuple


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format and security.
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL is required"
    
    url = url.strip()
    
    if not url:
        return False, "URL cannot be empty"
    
    try:
        parsed = urlparse(url)
        
        # Check protocol
        if parsed.scheme not in ['http', 'https']:
            return False, "URL must use HTTP or HTTPS protocol"
        
        # Check if hostname exists
        if not parsed.netloc:
            return False, "URL must have a valid hostname"
        
        # Security checks - block localhost and private IPs
        hostname = parsed.hostname
        if hostname:
            hostname = hostname.lower()
            
            # Block localhost
            if hostname in ['localhost', '127.0.0.1', '::1']:
                return False, "Access to localhost is not allowed"
            
            # Block private IP ranges (basic check)
            if hostname.startswith('192.168.') or hostname.startswith('10.') or hostname.startswith('172.'):
                return False, "Access to private IP addresses is not allowed"
            
            # Block file:// and other protocols
            if parsed.scheme not in ['http', 'https']:
                return False, "Only HTTP and HTTPS protocols are allowed"
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_config(config: dict) -> Tuple[bool, List[str]]:
    """
    Validate crawl configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate word count threshold
    word_threshold = config.get('word_count_threshold', 200)
    if not isinstance(word_threshold, int) or word_threshold < 1:
        errors.append("word_count_threshold must be a positive integer")
    elif word_threshold > 10000:
        errors.append("word_count_threshold cannot exceed 10000")
    
    # Validate extraction strategy
    extraction_strategy = config.get('extraction_strategy', 'default')
    valid_strategies = ['default', 'llm', 'css', 'regex']
    if extraction_strategy not in valid_strategies:
        errors.append(f"extraction_strategy must be one of: {valid_strategies}")
    
    # Validate CSS selector if provided
    css_selector = config.get('css_selector')
    if css_selector is not None:
        if not isinstance(css_selector, str):
            errors.append("css_selector must be a string")
        elif len(css_selector.strip()) == 0:
            # Empty selector is OK, will be ignored
            pass
        else:
            # Basic CSS selector validation
            if not is_valid_css_selector(css_selector):
                errors.append("css_selector contains invalid characters")
    
    # Validate timeout
    timeout = config.get('timeout', 30)
    if not isinstance(timeout, int) or timeout < 5:
        errors.append("timeout must be at least 5 seconds")
    elif timeout > 300:
        errors.append("timeout cannot exceed 300 seconds")
    
    # Validate boolean fields
    boolean_fields = [
        'screenshot', 'pdf', 'remove_overlay_elements',
        'exclude_external_links', 'exclude_social_media_links'
    ]
    
    for field in boolean_fields:
        value = config.get(field)
        if value is not None and not isinstance(value, bool):
            errors.append(f"{field} must be a boolean value")
    
    # Validate headers if provided
    headers = config.get('headers')
    if headers is not None:
        if not isinstance(headers, dict):
            errors.append("headers must be a dictionary")
        else:
            for key, value in headers.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append("headers keys and values must be strings")
                    break
    
    return len(errors) == 0, errors


def is_valid_css_selector(selector: str) -> bool:
    """
    Basic CSS selector validation.
    
    Args:
        selector: CSS selector string
        
    Returns:
        True if selector appears valid
    """
    if not selector or not isinstance(selector, str):
        return False
    
    # Remove whitespace
    selector = selector.strip()
    
    if not selector:
        return False
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '`', '\n', '\r', '\t']
    for char in dangerous_chars:
        if char in selector:
            return False
    
    # Basic pattern check - allow common CSS selector characters
    pattern = r'^[a-zA-Z0-9\s\.\#\[\]\(\)\:\-_,>+~=\*\^$|"\']+$'
    
    return bool(re.match(pattern, selector))


def validate_batch_urls(urls: List[str], max_urls: int = 10) -> Tuple[bool, List[str]]:
    """
    Validate a batch of URLs.
    
    Args:
        urls: List of URL strings
        max_urls: Maximum number of URLs allowed
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(urls, list):
        return False, ["URLs must be provided as a list"]
    
    if len(urls) == 0:
        return False, ["At least one URL is required"]
    
    if len(urls) > max_urls:
        return False, [f"Maximum {max_urls} URLs allowed per batch"]
    
    # Validate each URL
    for i, url in enumerate(urls):
        is_valid, error = validate_url(url)
        if not is_valid:
            errors.append(f"URL {i+1}: {error}")
    
    return len(errors) == 0, errors


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Strip whitespace
    text = text.strip()
    
    return text
