# Crawl4AI Web Application API Documentation

## Overview

The Crawl4AI Web Application provides a comprehensive RESTful API for web crawling and content extraction. The API is built with FastAPI and provides both synchronous and asynchronous crawling capabilities.

## Base URL

```
http://localhost:8080/api/v1
```

## Authentication

The API supports optional API key authentication. You can use the API without authentication, but API keys provide additional features like usage tracking and rate limiting.

### API Key Header
```
X-API-Key: your_api_key_here
```

## API Endpoints

### 🔍 Crawling Endpoints

#### POST /api/v1/crawl/
Create a new crawl task (asynchronous).

**Request Body:**
```json
{
  "url": "https://example.com",
  "config": {
    "extraction_strategy": "default",
    "word_count_threshold": 200,
    "css_selector": "",
    "include_links": true,
    "include_images": true,
    "take_screenshot": false
  },
  "options": {
    "priority": "normal",
    "callback_url": ""
  }
}
```

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "pending",
  "progress": 0.0,
  "created_at": "2025-06-15T10:00:00Z",
  "updated_at": "2025-06-15T10:00:00Z",
  "config": {...}
}
```

#### GET /api/v1/crawl/{task_id}
Get the status and result of a crawl task.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "progress": 100.0,
  "created_at": "2025-06-15T10:00:00Z",
  "updated_at": "2025-06-15T10:01:30Z",
  "result": {
    "url": "https://example.com",
    "title": "Page Title",
    "markdown": "# Content in markdown...",
    "html": "<html>...</html>",
    "text": "Plain text content...",
    "links": [...],
    "images": [...],
    "metadata": {...},
    "crawl_time": 1.5,
    "content_size": 1024
  }
}
```

#### POST /api/v1/crawl/quick
Perform a synchronous crawl with timeout.

**Query Parameters:**
- `timeout`: Maximum time to wait (5-300 seconds, default: 30)

**Request Body:** Same as POST /api/v1/crawl/

**Response:**
```json
{
  "success": true,
  "task_id": "uuid-string",
  "result": {...},
  "crawl_time": 1.5
}
```

#### POST /api/v1/crawl/batch
Create multiple crawl tasks at once.

**Request Body:**
```json
{
  "urls": [
    "https://example1.com",
    "https://example2.com"
  ],
  "config": {...},
  "options": {...}
}
```

**Response:**
```json
{
  "batch_id": "uuid-string",
  "task_ids": ["uuid1", "uuid2"],
  "total_tasks": 2,
  "status": "created"
}
```

#### GET /api/v1/crawl/
List crawl tasks with pagination and filtering.

**Query Parameters:**
- `status`: Filter by status (pending, running, completed, failed)
- `limit`: Maximum results (1-1000, default: 50)
- `offset`: Skip results (default: 0)

**Response:**
```json
{
  "tasks": [...],
  "total": 100,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

#### DELETE /api/v1/crawl/{task_id}
Cancel a running crawl task.

**Response:**
```json
{
  "message": "Task uuid cancelled successfully"
}
```

#### GET /api/v1/crawl/{task_id}/result
Get task result in specific format.

**Query Parameters:**
- `format`: Result format (json, markdown, html, text)

**Response:** Content in requested format

#### GET /api/v1/crawl/{task_id}/download
Download task result as a file.

**Query Parameters:**
- `format`: File format (json, markdown, html, text)

**Response:** File download

#### POST /api/v1/crawl/validate
Validate a crawl request without executing it.

**Request Body:** Same as POST /api/v1/crawl/

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["URL is very long, may cause issues"],
  "url_info": {
    "scheme": "https",
    "domain": "example.com",
    "path": "/page"
  }
}
```

#### GET /api/v1/crawl/stats
Get crawling statistics.

**Response:**
```json
{
  "total_tasks": 1000,
  "status_breakdown": {
    "completed": 800,
    "failed": 50,
    "running": 10,
    "pending": 140
  },
  "success_rate": 94.1,
  "average_crawl_time": 2.3,
  "total_pages_crawled": 1000,
  "last_24h_tasks": 150
}
```

### ⚙️ Configuration Endpoints

#### GET /api/v1/config/defaults
Get default configuration values.

**Response:**
```json
{
  "extraction_strategy": "default",
  "word_count_threshold": 200,
  "css_selector": "",
  "include_links": true,
  "include_images": true,
  "take_screenshot": false
}
```

#### GET /api/v1/config/strategies
Get available extraction strategies.

**Response:**
```json
{
  "strategies": [
    {
      "name": "default",
      "description": "Standard content extraction",
      "parameters": []
    },
    {
      "name": "css",
      "description": "CSS selector-based extraction",
      "parameters": ["css_selector"]
    }
  ]
}
```

### 🔐 Authentication Endpoints

#### POST /api/v1/auth/generate-key
Generate a new API key.

**Request Body:**
```json
{
  "name": "My API Key",
  "description": "For my application",
  "expires_in_days": 30
}
```

**Response:**
```json
{
  "api_key": "crawl4ai_...",
  "name": "My API Key",
  "created_at": "2025-06-15T10:00:00Z",
  "expires_at": "2025-07-15T10:00:00Z",
  "message": "API key generated successfully..."
}
```

#### GET /api/v1/auth/keys
List all API keys (without showing actual keys).

#### DELETE /api/v1/auth/keys/{key_hash}
Revoke an API key.

#### GET /api/v1/auth/verify
Verify the current API key.

### 🏥 Health Endpoints

#### GET /api/v1/health/
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-15T10:00:00Z",
  "service": "Crawl4AI Web Application",
  "version": "1.0.0"
}
```

#### GET /api/v1/health/detailed
Detailed health check with system information.

#### GET /api/v1/health/metrics
System performance metrics.

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `408` - Request Timeout
- `429` - Too Many Requests
- `500` - Internal Server Error

## Rate Limiting

API requests are rate-limited to prevent abuse:
- Without API key: 100 requests per hour
- With API key: 1000 requests per hour
- Quick crawl: 10 requests per minute

## Error Response Format

```json
{
  "detail": "Error description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-15T10:00:00Z"
}
```

## WebSocket API

Real-time updates are available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Task update:', data);
};
```

## Interactive Documentation

Visit `/docs` for interactive API documentation with Swagger UI.
Visit `/redoc` for alternative documentation with ReDoc.
