# Crawl4AI API Quick Start Guide

Get started with the Crawl4AI Web Application API in minutes!

## 🚀 Quick Setup

1. **Start the server**
   ```bash
   cd crawl4ai-web
   python run.py
   ```

2. **Verify it's running**
   ```bash
   curl http://localhost:8080/api/v1/health/
   ```

## 📝 Basic Usage

### 1. Simple Crawl (Synchronous)

The fastest way to crawl a webpage:

```bash
curl -X POST "http://localhost:8080/api/v1/crawl/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "config": {
      "extraction_strategy": "default",
      "word_count_threshold": 100
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "task_id": "uuid-here",
  "result": {
    "title": "Example Domain",
    "markdown": "# Example Domain\n\nThis domain is for use in illustrative examples...",
    "html": "<html>...</html>",
    "text": "Example Domain This domain is for use...",
    "crawl_time": 1.2
  }
}
```

### 2. Asynchronous Crawl

For longer crawls or when you need to track progress:

```bash
# Step 1: Create task
TASK_ID=$(curl -X POST "http://localhost:8080/api/v1/crawl/" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "config": {
      "extraction_strategy": "default",
      "word_count_threshold": 200
    }
  }' | jq -r '.task_id')

# Step 2: Check status
curl "http://localhost:8080/api/v1/crawl/$TASK_ID"

# Step 3: Get result when completed
curl "http://localhost:8080/api/v1/crawl/$TASK_ID/result"
```

### 3. Download Results

```bash
# Download as markdown
curl "http://localhost:8080/api/v1/crawl/$TASK_ID/download?format=markdown" \
  -o result.md

# Download as JSON
curl "http://localhost:8080/api/v1/crawl/$TASK_ID/download?format=json" \
  -o result.json
```

## 🎯 Common Use Cases

### Extract Specific Content with CSS Selectors

```bash
curl -X POST "http://localhost:8080/api/v1/crawl/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.ycombinator.com",
    "config": {
      "extraction_strategy": "css",
      "css_selector": ".storylink",
      "word_count_threshold": 10
    }
  }'
```

### Crawl Multiple URLs at Once

```bash
curl -X POST "http://localhost:8080/api/v1/crawl/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com",
      "https://httpbin.org/html",
      "https://quotes.toscrape.com"
    ],
    "config": {
      "extraction_strategy": "default",
      "word_count_threshold": 150
    }
  }'
```

### Get Crawling Statistics

```bash
curl "http://localhost:8080/api/v1/crawl/stats"
```

## 🔑 Using API Keys (Optional)

### Generate an API Key

```bash
curl -X POST "http://localhost:8080/api/v1/auth/generate-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My App",
    "description": "API key for my application",
    "expires_in_days": 30
  }'
```

### Use API Key in Requests

```bash
curl -X POST "http://localhost:8080/api/v1/crawl/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "url": "https://example.com",
    "config": {
      "extraction_strategy": "default"
    }
  }'
```

## 🐍 Python Quick Start

```python
import requests

# Base URL
BASE_URL = "http://localhost:8080/api/v1"

# Quick crawl
def quick_crawl(url):
    response = requests.post(f"{BASE_URL}/crawl/quick", json={
        "url": url,
        "config": {
            "extraction_strategy": "default",
            "word_count_threshold": 100
        }
    })
    return response.json()

# Example usage
result = quick_crawl("https://example.com")
if result["success"]:
    print(f"Title: {result['result']['title']}")
    print(f"Content: {result['result']['markdown'][:200]}...")
```

## 🌐 JavaScript Quick Start

```javascript
const BASE_URL = 'http://localhost:8080/api/v1';

async function quickCrawl(url) {
    const response = await fetch(`${BASE_URL}/crawl/quick`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            url: url,
            config: {
                extraction_strategy: 'default',
                word_count_threshold: 100
            }
        })
    });
    return await response.json();
}

// Example usage
quickCrawl('https://example.com')
    .then(result => {
        if (result.success) {
            console.log('Title:', result.result.title);
            console.log('Content:', result.result.markdown.substring(0, 200));
        }
    });
```

## 📊 Monitoring and Health Checks

### Basic Health Check
```bash
curl "http://localhost:8080/api/v1/health/"
```

### Detailed System Information
```bash
curl "http://localhost:8080/api/v1/health/detailed"
```

### System Metrics
```bash
curl "http://localhost:8080/api/v1/health/metrics"
```

## 🔧 Configuration Options

### Extraction Strategies

- **`default`**: Standard content extraction
- **`css`**: CSS selector-based extraction
- **`llm`**: AI-powered content extraction (requires OpenAI API key)

### Common Parameters

- **`word_count_threshold`**: Minimum words per content block (default: 200)
- **`include_links`**: Extract page links (default: true)
- **`include_images`**: Extract image information (default: true)
- **`take_screenshot`**: Capture page screenshot (default: false)

### Example with All Options

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

## 🚨 Error Handling

### Common HTTP Status Codes

- **200**: Success
- **400**: Bad Request (invalid URL or parameters)
- **404**: Task not found
- **408**: Request timeout
- **429**: Rate limit exceeded
- **500**: Internal server error

### Example Error Response

```json
{
  "detail": "Invalid URL format",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-15T10:00:00Z"
}
```

## 📚 Next Steps

1. **Explore the full API documentation**: Visit `/docs` for interactive documentation
2. **Import Postman collection**: Use the provided Postman collection for testing
3. **Check out examples**: See `API_EXAMPLES.md` for more detailed examples
4. **Monitor your usage**: Use the statistics endpoint to track your API usage

## 🆘 Need Help?

- **Interactive API docs**: http://localhost:8080/docs
- **Health check**: http://localhost:8080/api/v1/health/
- **GitHub Issues**: Report bugs or request features
- **API Examples**: Check `docs/API_EXAMPLES.md` for more examples

Happy crawling! 🕷️✨
