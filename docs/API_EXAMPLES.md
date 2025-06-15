# API Usage Examples

This document provides practical examples of how to use the Crawl4AI Web Application API.

## Python Examples

### Basic Crawling

```python
import requests
import time

# API base URL
BASE_URL = "http://localhost:8080/api/v1"

# Create a crawl task
def create_crawl_task(url):
    response = requests.post(f"{BASE_URL}/crawl/", json={
        "url": url,
        "config": {
            "extraction_strategy": "default",
            "word_count_threshold": 200,
            "include_links": True,
            "include_images": True
        }
    })
    return response.json()

# Check task status
def get_task_status(task_id):
    response = requests.get(f"{BASE_URL}/crawl/{task_id}")
    return response.json()

# Example usage
task = create_crawl_task("https://example.com")
task_id = task["task_id"]

# Poll for completion
while True:
    status = get_task_status(task_id)
    print(f"Status: {status['status']}, Progress: {status['progress']}%")
    
    if status["status"] in ["completed", "failed"]:
        break
    
    time.sleep(2)

if status["status"] == "completed":
    print("Crawl completed!")
    print(f"Title: {status['result']['title']}")
    print(f"Content size: {status['result']['content_size']} characters")
```

### Quick Synchronous Crawl

```python
import requests

def quick_crawl(url, timeout=30):
    response = requests.post(f"{BASE_URL}/crawl/quick", 
        json={
            "url": url,
            "config": {
                "extraction_strategy": "default",
                "word_count_threshold": 100
            }
        },
        params={"timeout": timeout}
    )
    return response.json()

# Example usage
result = quick_crawl("https://example.com")
if result["success"]:
    print(f"Title: {result['result']['title']}")
    print(f"Markdown content: {result['result']['markdown'][:200]}...")
else:
    print(f"Crawl failed: {result['error']}")
```

### Batch Crawling

```python
import requests

def batch_crawl(urls):
    response = requests.post(f"{BASE_URL}/crawl/batch", json={
        "urls": urls,
        "config": {
            "extraction_strategy": "default",
            "word_count_threshold": 150
        }
    })
    return response.json()

# Example usage
urls = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://quotes.toscrape.com"
]

batch = batch_crawl(urls)
print(f"Created {batch['total_tasks']} tasks")

# Monitor all tasks
for task_id in batch["task_ids"]:
    while True:
        status = get_task_status(task_id)
        if status["status"] in ["completed", "failed"]:
            print(f"Task {task_id}: {status['status']}")
            break
        time.sleep(1)
```

### CSS Selector Extraction

```python
def crawl_with_css_selector(url, selector):
    response = requests.post(f"{BASE_URL}/crawl/", json={
        "url": url,
        "config": {
            "extraction_strategy": "css",
            "css_selector": selector,
            "word_count_threshold": 10
        }
    })
    return response.json()

# Example: Extract all article titles from Hacker News
task = crawl_with_css_selector(
    "https://news.ycombinator.com",
    ".storylink"
)

# Wait for completion and get results
task_id = task["task_id"]
while True:
    status = get_task_status(task_id)
    if status["status"] == "completed":
        print("Extracted content:")
        print(status["result"]["markdown"])
        break
    elif status["status"] == "failed":
        print(f"Failed: {status['error']}")
        break
    time.sleep(2)
```

### Download Results

```python
def download_result(task_id, format="json"):
    response = requests.get(f"{BASE_URL}/crawl/{task_id}/download", 
                          params={"format": format})
    
    if response.status_code == 200:
        filename = f"crawl_result_{task_id}.{format}"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    else:
        print(f"Download failed: {response.status_code}")

# Example usage
download_result(task_id, "markdown")
download_result(task_id, "json")
```

## JavaScript Examples

### Basic Fetch API

```javascript
const BASE_URL = 'http://localhost:8080/api/v1';

// Create crawl task
async function createCrawlTask(url) {
    const response = await fetch(`${BASE_URL}/crawl/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
            config: {
                extraction_strategy: 'default',
                word_count_threshold: 200,
                include_links: true
            }
        })
    });
    return await response.json();
}

// Check task status
async function getTaskStatus(taskId) {
    const response = await fetch(`${BASE_URL}/crawl/${taskId}`);
    return await response.json();
}

// Example usage
async function crawlExample() {
    try {
        const task = await createCrawlTask('https://example.com');
        console.log('Task created:', task.task_id);
        
        // Poll for completion
        while (true) {
            const status = await getTaskStatus(task.task_id);
            console.log(`Status: ${status.status}, Progress: ${status.progress}%`);
            
            if (status.status === 'completed') {
                console.log('Crawl completed!');
                console.log('Title:', status.result.title);
                break;
            } else if (status.status === 'failed') {
                console.log('Crawl failed:', status.error);
                break;
            }
            
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

crawlExample();
```

### Using Axios

```javascript
const axios = require('axios');

const api = axios.create({
    baseURL: 'http://localhost:8080/api/v1',
    headers: {
        'Content-Type': 'application/json'
    }
});

// Quick crawl with axios
async function quickCrawl(url) {
    try {
        const response = await api.post('/crawl/quick', {
            url: url,
            config: {
                extraction_strategy: 'default',
                word_count_threshold: 100
            }
        }, {
            params: { timeout: 30 }
        });
        
        return response.data;
    } catch (error) {
        console.error('Quick crawl failed:', error.response?.data || error.message);
        throw error;
    }
}

// Example usage
quickCrawl('https://example.com')
    .then(result => {
        if (result.success) {
            console.log('Title:', result.result.title);
            console.log('Content preview:', result.result.markdown.substring(0, 200));
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
```

## cURL Examples

### Basic Crawl

```bash
# Create crawl task
curl -X POST "http://localhost:8080/api/v1/crawl/" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "config": {
      "extraction_strategy": "default",
      "word_count_threshold": 200
    }
  }'

# Check task status (replace TASK_ID with actual ID)
curl "http://localhost:8080/api/v1/crawl/TASK_ID"

# Download result as markdown
curl "http://localhost:8080/api/v1/crawl/TASK_ID/download?format=markdown" \
  -o result.md
```

### Quick Crawl

```bash
curl -X POST "http://localhost:8080/api/v1/crawl/quick?timeout=30" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "config": {
      "extraction_strategy": "default",
      "word_count_threshold": 100
    }
  }'
```

### With API Key

```bash
curl -X POST "http://localhost:8080/api/v1/crawl/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "url": "https://example.com",
    "config": {
      "extraction_strategy": "css",
      "css_selector": "article",
      "word_count_threshold": 50
    }
  }'
```

## Error Handling Examples

### Python Error Handling

```python
import requests
from requests.exceptions import RequestException

def safe_crawl(url):
    try:
        response = requests.post(f"{BASE_URL}/crawl/", 
            json={
                "url": url,
                "config": {
                    "extraction_strategy": "default",
                    "word_count_threshold": 200
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            print(f"Bad request: {response.json()['detail']}")
        elif response.status_code == 429:
            print("Rate limit exceeded. Please wait.")
        else:
            print(f"Unexpected error: {response.status_code}")
            
    except RequestException as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None
```

### JavaScript Error Handling

```javascript
async function safeCrawl(url) {
    try {
        const response = await fetch(`${BASE_URL}/crawl/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                config: {
                    extraction_strategy: 'default',
                    word_count_threshold: 200
                }
            })
        });
        
        if (response.ok) {
            return await response.json();
        } else if (response.status === 400) {
            const error = await response.json();
            console.error('Bad request:', error.detail);
        } else if (response.status === 429) {
            console.error('Rate limit exceeded');
        } else {
            console.error('Unexpected error:', response.status);
        }
    } catch (error) {
        console.error('Network error:', error);
    }
    
    return null;
}
```

## Best Practices

1. **Always handle errors gracefully**
2. **Use appropriate timeouts for your use case**
3. **Implement exponential backoff for retries**
4. **Validate URLs before sending requests**
5. **Use batch operations for multiple URLs**
6. **Monitor your API usage with statistics endpoint**
7. **Store API keys securely**
8. **Use appropriate extraction strategies for your content type**
