"""
Crawler service for managing crawl tasks
"""

import asyncio
import time
from typing import Dict, Optional, List
from datetime import datetime
import traceback
import base64

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("⚠️ Crawl4AI not available, using mock implementation")

from app.models.request import CrawlRequestModel
from app.models.response import TaskResponseModel, TaskStatus, CrawlResultModel


class CrawlerService:
    """Service for managing crawl tasks."""
    
    def __init__(self):
        self.tasks: Dict[str, TaskResponseModel] = {}
        self.crawler = None
        self._lock = asyncio.Lock()
    
    async def _get_crawler(self):
        """Get or create crawler instance."""
        if not CRAWL4AI_AVAILABLE:
            return None

        if self.crawler is None:
            browser_config = BrowserConfig(
                headless=True,
                verbose=False
            )
            self.crawler = AsyncWebCrawler(config=browser_config)
            await self.crawler.start()
        return self.crawler
    
    async def create_task(
        self, 
        task_id: str, 
        request: CrawlRequestModel, 
        task_response: TaskResponseModel
    ):
        """Create a new crawl task."""
        async with self._lock:
            self.tasks[task_id] = task_response
    
    async def get_task(self, task_id: str) -> Optional[TaskResponseModel]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    async def list_tasks(
        self, 
        status: str = None, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[TaskResponseModel]:
        """List tasks with optional filtering."""
        tasks = list(self.tasks.values())
        
        # Filter by status if provided
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        # Sort by creation time (newest first)
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return tasks[offset:offset + limit]
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.updated_at = datetime.now()
            return True
        
        return False
    
    async def execute_crawl_task(self, task_id: str, request: CrawlRequestModel):
        """Execute a crawl task."""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            # Update task status to running
            task.status = TaskStatus.RUNNING
            task.progress = 0.1
            task.updated_at = datetime.now()
            
            # Broadcast update (if WebSocket is available)
            await self._broadcast_task_update(task_id, task)
            
            # Get crawler instance
            crawler = await self._get_crawler()

            # Update progress
            task.progress = 0.3
            task.updated_at = datetime.now()
            await self._broadcast_task_update(task_id, task)

            # Execute crawl
            start_time = time.time()

            if CRAWL4AI_AVAILABLE and crawler:
                # Real Crawl4AI implementation
                crawl_config = self._convert_config(request.config)
                result = await crawler.arun(
                    url=str(request.url),
                    config=crawl_config
                )
            else:
                # Mock implementation for testing
                result = await self._mock_crawl(str(request.url), request.config)

            crawl_time = time.time() - start_time
            
            # Update progress
            task.progress = 0.8
            task.updated_at = datetime.now()
            await self._broadcast_task_update(task_id, task)
            
            # Convert result to our model
            crawl_result = self._convert_result(result, str(request.url), crawl_time)
            
            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            task.result = crawl_result
            task.updated_at = datetime.now()
            task.completed_at = datetime.now()
            
            # Broadcast completion
            await self._broadcast_task_completed(task_id, task)
            
        except Exception as e:
            # Handle error
            error_message = str(e)
            error_details = {
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
            
            task.status = TaskStatus.FAILED
            task.error = error_message
            task.error_details = error_details
            task.updated_at = datetime.now()
            task.completed_at = datetime.now()
            
            # Broadcast error
            await self._broadcast_task_error(task_id, task)
    
    async def _mock_crawl(self, url: str, config):
        """Mock crawl implementation for testing when Crawl4AI is not available."""
        import asyncio
        import aiohttp
        from bs4 import BeautifulSoup

        # Simulate crawling delay
        await asyncio.sleep(2)

        try:
            # Fetch the page
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    html_content = await response.text()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text_content = soup.get_text()
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)

            # Create simple markdown
            markdown_content = f"# {title_text}\n\n{text_content[:2000]}..."

            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                links.append({
                    'url': link['href'],
                    'text': link.get_text().strip()
                })

            # Create mock result object
            class MockResult:
                def __init__(self):
                    self.title = title_text
                    self.markdown = markdown_content
                    self.cleaned_html = str(soup)[:5000] + "..." if len(str(soup)) > 5000 else str(soup)
                    self.text = text_content
                    self.extracted_content = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
                    self.screenshot = None
                    self.links = {'internal': links[:10]}  # Limit to 10 links
                    self.media = {'images': []}
                    self.metadata = {
                        'url': url,
                        'status_code': response.status,
                        'content_type': response.headers.get('content-type', ''),
                        'mock_crawl': True
                    }

            return MockResult()

        except Exception as e:
            # Return error result
            class ErrorResult:
                def __init__(self, error_msg):
                    self.title = "Error"
                    self.markdown = f"# Error\n\nFailed to crawl {url}: {error_msg}"
                    self.cleaned_html = f"<p>Error: {error_msg}</p>"
                    self.text = f"Error: {error_msg}"
                    self.extracted_content = f"Error: {error_msg}"
                    self.screenshot = None
                    self.links = {'internal': []}
                    self.media = {'images': []}
                    self.metadata = {'url': url, 'error': str(e), 'mock_crawl': True}

            return ErrorResult(str(e))

    def _convert_result(self, result, url: str, crawl_time: float) -> CrawlResultModel:
        """Convert crawl result to our model."""
        # Process images to ensure correct data types
        images = []
        if hasattr(result, 'media') and result.media and 'images' in result.media:
            for img in result.media['images']:
                if isinstance(img, dict):
                    # Convert problematic fields to strings
                    processed_img = {}
                    for key, value in img.items():
                        if value is None:
                            processed_img[key] = ""
                        elif isinstance(value, (int, float)):
                            processed_img[key] = str(value)
                        else:
                            processed_img[key] = str(value) if value is not None else ""
                    images.append(processed_img)
                else:
                    images.append({"url": str(img), "alt": "", "title": ""})

        # Process links to ensure correct format
        links = []
        if hasattr(result, 'links') and result.links and 'internal' in result.links:
            for link in result.links['internal']:
                if isinstance(link, dict):
                    links.append({
                        'url': str(link.get('url', '')),
                        'text': str(link.get('text', ''))
                    })
                else:
                    links.append({'url': str(link), 'text': ''})

        # Ensure metadata is always a dictionary
        metadata = getattr(result, 'metadata', None)
        if metadata is None:
            metadata = {}
        elif not isinstance(metadata, dict):
            metadata = {}

        return CrawlResultModel(
            url=url,
            title=getattr(result, 'title', None),
            markdown=getattr(result, 'markdown', None),
            html=getattr(result, 'cleaned_html', None),
            text=getattr(result, 'text', None),
            extracted_content=getattr(result, 'extracted_content', None),
            screenshot=getattr(result, 'screenshot', None),
            links=links,
            images=images,
            metadata=metadata,
            crawl_time=crawl_time,
            content_size=len(getattr(result, 'markdown', '') or '')
        )

    def _convert_config(self, config):
        """Convert our config model to Crawl4AI config."""
        if not CRAWL4AI_AVAILABLE:
            return None

        crawl_config = CrawlerRunConfig(
            word_count_threshold=config.word_count_threshold,
            css_selector=config.css_selector,
            screenshot=config.screenshot,
            cache_mode=CacheMode.BYPASS,  # Always bypass cache for web app
            remove_overlay_elements=config.remove_overlay_elements,
            exclude_external_links=config.exclude_external_links,
            exclude_social_media_links=config.exclude_social_media_links,
        )
        
        # Set wait condition if provided
        if config.wait_for:
            if config.wait_for.isdigit():
                crawl_config.wait_for = int(config.wait_for)
            else:
                crawl_config.wait_for = config.wait_for
        
        # Set extraction strategy
        if config.extraction_strategy == "llm":
            # Note: LLM extraction would require additional setup
            pass
        elif config.extraction_strategy == "css":
            # CSS extraction is handled by css_selector
            pass
        elif config.extraction_strategy == "regex":
            # Note: Regex extraction would require additional setup
            pass
        
        return crawl_config
    
    async def _broadcast_task_update(self, task_id: str, task: TaskResponseModel):
        """Broadcast task update via WebSocket."""
        try:
            # Import here to avoid circular imports
            from app.api.websocket import broadcast_task_update
            await broadcast_task_update(
                task_id=task_id,
                status=task.status,
                progress=task.progress,
                data={
                    "updated_at": task.updated_at.isoformat()
                }
            )
        except Exception:
            # Ignore WebSocket errors
            pass
    
    async def _broadcast_task_completed(self, task_id: str, task: TaskResponseModel):
        """Broadcast task completion via WebSocket."""
        try:
            from app.api.websocket import broadcast_task_completed
            await broadcast_task_completed(
                task_id=task_id,
                result=task.result.dict() if task.result else {}
            )
        except Exception:
            pass
    
    async def _broadcast_task_error(self, task_id: str, task: TaskResponseModel):
        """Broadcast task error via WebSocket."""
        try:
            from app.api.websocket import broadcast_task_error
            await broadcast_task_error(
                task_id=task_id,
                error=task.error or "Unknown error"
            )
        except Exception:
            pass
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.crawler:
            await self.crawler.close()


# Global service instance
_crawler_service = None


def get_crawler_service() -> CrawlerService:
    """Get the global crawler service instance."""
    global _crawler_service
    if _crawler_service is None:
        _crawler_service = CrawlerService()
    return _crawler_service
