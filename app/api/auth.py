"""
Authentication and API key management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import os
from pathlib import Path

router = APIRouter()

# Simple file-based API key storage (for production, use a proper database)
API_KEYS_FILE = Path("api_keys.json")


def load_api_keys() -> Dict[str, Dict[str, Any]]:
    """Load API keys from file."""
    if not API_KEYS_FILE.exists():
        return {}
    
    try:
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_api_keys(keys: Dict[str, Dict[str, Any]]):
    """Save API keys to file."""
    try:
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys, f, indent=2, default=str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save API keys: {str(e)}")


def generate_api_key() -> str:
    """Generate a new API key."""
    return f"crawl4ai_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """
    Verify API key from header.
    This is optional - if no API key is provided, access is still allowed.
    """
    if not x_api_key:
        return None
    
    api_keys = load_api_keys()
    key_hash = hash_api_key(x_api_key)
    
    if key_hash in api_keys:
        key_info = api_keys[key_hash]
        
        # Check if key is expired
        if key_info.get('expires_at'):
            expires_at = datetime.fromisoformat(key_info['expires_at'])
            if datetime.now() > expires_at:
                raise HTTPException(status_code=401, detail="API key expired")
        
        # Update last used
        key_info['last_used'] = datetime.now().isoformat()
        key_info['usage_count'] = key_info.get('usage_count', 0) + 1
        save_api_keys(api_keys)
        
        return key_info
    
    raise HTTPException(status_code=401, detail="Invalid API key")


@router.post("/generate-key", summary="Generate new API key")
async def generate_new_api_key(
    name: str,
    description: str = "",
    expires_in_days: Optional[int] = None
):
    """
    Generate a new API key.
    
    Args:
        name: Name for the API key
        description: Description of the API key usage
        expires_in_days: Number of days until expiration (optional)
    
    Returns:
        dict: New API key information
    """
    try:
        api_key = generate_api_key()
        key_hash = hash_api_key(api_key)
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        key_info = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "last_used": None,
            "usage_count": 0,
            "active": True
        }
        
        # Save to storage
        api_keys = load_api_keys()
        api_keys[key_hash] = key_info
        save_api_keys(api_keys)
        
        return {
            "api_key": api_key,
            "name": name,
            "description": description,
            "created_at": key_info["created_at"],
            "expires_at": expires_at,
            "message": "API key generated successfully. Store it securely - it won't be shown again."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate API key: {str(e)}")


@router.get("/keys", summary="List API keys")
async def list_api_keys():
    """
    List all API keys (without showing the actual keys).
    
    Returns:
        dict: List of API key information
    """
    try:
        api_keys = load_api_keys()
        
        keys_info = []
        for key_hash, info in api_keys.items():
            keys_info.append({
                "key_hash": key_hash[:16] + "...",  # Show partial hash
                "name": info["name"],
                "description": info["description"],
                "created_at": info["created_at"],
                "expires_at": info.get("expires_at"),
                "last_used": info.get("last_used"),
                "usage_count": info.get("usage_count", 0),
                "active": info.get("active", True)
            })
        
        return {
            "keys": keys_info,
            "total": len(keys_info)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list API keys: {str(e)}")


@router.delete("/keys/{key_hash}", summary="Revoke API key")
async def revoke_api_key(key_hash: str):
    """
    Revoke an API key.
    
    Args:
        key_hash: Hash of the API key to revoke
    
    Returns:
        dict: Confirmation message
    """
    try:
        api_keys = load_api_keys()
        
        if key_hash not in api_keys:
            raise HTTPException(status_code=404, detail="API key not found")
        
        # Mark as inactive instead of deleting
        api_keys[key_hash]["active"] = False
        api_keys[key_hash]["revoked_at"] = datetime.now().isoformat()
        save_api_keys(api_keys)
        
        return {"message": "API key revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke API key: {str(e)}")


@router.get("/verify", summary="Verify API key")
async def verify_current_api_key(
    key_info: Optional[Dict[str, Any]] = Depends(verify_api_key)
):
    """
    Verify the current API key.
    
    Returns:
        dict: API key information if valid
    """
    if not key_info:
        return {"message": "No API key provided", "authenticated": False}
    
    return {
        "message": "API key is valid",
        "authenticated": True,
        "key_info": {
            "name": key_info["name"],
            "description": key_info["description"],
            "created_at": key_info["created_at"],
            "expires_at": key_info.get("expires_at"),
            "usage_count": key_info.get("usage_count", 0)
        }
    }
