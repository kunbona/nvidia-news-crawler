"""
Base crawler class - Abstract base for all crawlers
"""
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger
from crawl4ai import AsyncWebCrawler


class BaseCrawler(ABC):
    """Base class for all crawlers"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize crawler
        
        Args:
            name: Crawler name
            config: Configuration dictionary
        """
        self.name = name
        self.config = config
        self.url = config.get("url", "")
        self.timeout = config.get("timeout", 30)
        self.retry_times = config.get("retry_times", 3)
        self.logger = logger.bind(name=self.name)
        
    async def async_crawl(self) -> List[Dict[str, Any]]:
        """
        Asynchronously crawl data
        
        Returns:
            List of crawled data dictionaries
        """
        self.logger.info(f"Starting {self.name} crawler")
        
        crawler = AsyncWebCrawler()
        for attempt in range(self.retry_times):
            try:
                result = await crawler.arun(
                    url=self.url,
                    timeout=self.timeout
                )
                self.logger.info(f"{self.name} crawler completed successfully")
                return await self.extract_data(result.markdown)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.retry_times - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    self.logger.error(f"{self.name} crawler failed after {self.retry_times} attempts")
                    return []
    
    def crawl(self) -> List[Dict[str, Any]]:
        """
        Synchronously crawl data
        
        Returns:
            List of crawled data dictionaries
        """
        return asyncio.run(self.async_crawl())
    
    @abstractmethod
    async def extract_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract data from HTML content
        
        Args:
            html_content: HTML content to extract
            
        Returns:
            List of extracted data dictionaries
        """
        pass
    
    def _normalize_date(self, date_str: str) -> Optional[datetime]:
        """
        Normalize date string to datetime
        
        Args:
            date_str: Date string
            
        Returns:
            datetime object or None
        """
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except Exception as e:
            self.logger.warning(f"Failed to parse date '{date_str}': {str(e)}")
            return None
    
    def _create_article(
        self,
        title: str,
        url: str,
        content: str = "",
        summary: str = "",
        publish_date: Optional[datetime] = None,
        author: str = "",
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Create article dictionary
        
        Args:
            title: Article title
            url: Article URL
            content: Article content
            summary: Article summary
            publish_date: Publication date
            author: Author name
            tags: List of tags
            
        Returns:
            Article dictionary
        """
        return {
            "title": title,
            "url": url,
            "content": content,
            "summary": summary,
            "publish_date": publish_date or datetime.now(),
            "author": author,
            "tags": tags or [],
            "source": self.name,
            "crawled_at": datetime.now(),
        }
