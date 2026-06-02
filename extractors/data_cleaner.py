"""
Data cleaning and deduplication
"""
from typing import List, Dict, Any, Set
from datetime import datetime
from loguru import logger
import hashlib


class DataCleaner:
    """Clean and deduplicate crawled data"""
    
    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()
    
    @staticmethod
    def _generate_hash(article: Dict[str, Any]) -> str:
        """
        Generate hash for article based on title and URL
        
        Args:
            article: Article dictionary
            
        Returns:
            Hash string
        """
        text = f"{article.get('title', '')}:{article.get('url', '')}"
        return hashlib.md5(text.encode()).hexdigest()
    
    def is_duplicate(self, article: Dict[str, Any]) -> bool:
        """
        Check if article is duplicate
        
        Args:
            article: Article dictionary
            
        Returns:
            True if duplicate, False otherwise
        """
        url = article.get("url", "")
        article_hash = self._generate_hash(article)
        
        if url in self.seen_urls or article_hash in self.seen_hashes:
            return True
        
        self.seen_urls.add(url)
        self.seen_hashes.add(article_hash)
        return False
    
    @staticmethod
    def remove_empty_fields(article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove empty or None fields
        
        Args:
            article: Article dictionary
            
        Returns:
            Cleaned article dictionary
        """
        return {k: v for k, v in article.items() if v}
    
    @staticmethod
    def validate_article(article: Dict[str, Any]) -> bool:
        """
        Validate article has required fields
        
        Args:
            article: Article dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["title", "url", "source"]
        return all(article.get(field) for field in required_fields)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text content
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        text = " ".join(text.split())
        text = text.replace("\n", " ").replace("\r", " ")
        
        return text.strip()
    
    def clean_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and deduplicate articles
        
        Args:
            articles: List of articles
            
        Returns:
            List of cleaned articles
        """
        cleaned = []
        
        for article in articles:
            try:
                if self.is_duplicate(article):
                    logger.debug(f"Skipped duplicate: {article.get('title', 'Unknown')}")
                    continue
                
                if not self.validate_article(article):
                    logger.warning(f"Invalid article, skipped: {article}")
                    continue
                
                article["title"] = self.clean_text(article.get("title", ""))
                article["content"] = self.clean_text(article.get("content", ""))
                article["summary"] = self.clean_text(article.get("summary", ""))
                
                article = self.remove_empty_fields(article)
                
                cleaned.append(article)
                
            except Exception as e:
                logger.error(f"Error cleaning article: {str(e)}")
                continue
        
        logger.info(f"Cleaned {len(cleaned)} articles from {len(articles)} total")
        return cleaned
