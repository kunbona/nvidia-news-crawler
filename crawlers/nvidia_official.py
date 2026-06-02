"""
NVIDIA Official news crawler
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class NvidiaOfficialCrawler(BaseCrawler):
    """Crawler for NVIDIA official news"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("nvidia_official", config)
    
    async def extract_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract news articles from NVIDIA news page
        
        Args:
            html_content: HTML content from NVIDIA news page
            
        Returns:
            List of news articles
        """
        articles = []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            selectors = self.config.get("selectors", {})
            article_container = selectors.get("article_container", "article")
            
            for article_elem in soup.select(article_container):
                try:
                    title_elem = article_elem.select_one(selectors.get("title", "h2"))
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    url_elem = article_elem.select_one(selectors.get("url", "a"))
                    url = url_elem.get("href", "") if url_elem else ""
                    
                    if url and not url.startswith("http"):
                        url = "https://www.nvidia.com" + url
                    
                    date_elem = article_elem.select_one(selectors.get("date", "span.date"))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    publish_date = self._normalize_date(date_str)
                    
                    content = article_elem.get_text(strip=True)
                    summary = content[:200] + "..." if len(content) > 200 else content
                    
                    if title and url:
                        article = self._create_article(
                            title=title,
                            url=url,
                            content=content,
                            summary=summary,
                            publish_date=publish_date,
                            tags=["nvidia", "official"]
                        )
                        articles.append(article)
                        self.logger.debug(f"Extracted article: {title}")
                
                except Exception as e:
                    self.logger.warning(f"Error extracting article: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(articles)} articles")
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {str(e)}")
        
        return articles
