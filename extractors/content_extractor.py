"""
Content extraction utility
"""
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
import hashlib


class ContentExtractor:
    """Extract and process content from crawled data"""
    
    @staticmethod
    def extract_metadata(article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from article
        
        Args:
            article: Article dictionary
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "title": article.get("title", "").strip(),
            "url": article.get("url", "").strip(),
            "source": article.get("source", "unknown"),
            "author": article.get("author", "").strip(),
            "publish_date": article.get("publish_date"),
            "crawled_at": article.get("crawled_at", datetime.now()),
            "tags": article.get("tags", []),
            "url_hash": hashlib.md5(article.get("url", "").encode()).hexdigest(),
        }
        return metadata
    
    @staticmethod
    def extract_text(article: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract text content from article
        
        Args:
            article: Article dictionary
            
        Returns:
            Text content dictionary
        """
        text_content = {
            "content": article.get("content", "").strip(),
            "summary": article.get("summary", "").strip(),
        }
        
        if not text_content["summary"] and text_content["content"]:
            content = text_content["content"]
            text_content["summary"] = (content[:200] + "...") if len(content) > 200 else content
        
        return text_content
    
    @staticmethod
    def normalize_article(article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize article data
        
        Args:
            article: Raw article dictionary
            
        Returns:
            Normalized article dictionary
        """
        normalized = {
            **ContentExtractor.extract_metadata(article),
            **ContentExtractor.extract_text(article),
        }
        
        return normalized
