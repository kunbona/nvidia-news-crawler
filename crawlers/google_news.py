"""
Google News crawler for NVIDIA related news
"""
from typing import List, Dict, Any
from urllib.parse import quote
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class GoogleNewsCrawler(BaseCrawler):
    """Crawler for NVIDIA related news from Google News"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("google_news", config)
        self.query = config.get("query", "NVIDIA")
        self.max_results = config.get("max_results", 50)
        self.url = f"https://news.google.com/search?q={quote(self.query)}"
    
    async def extract_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract news articles from Google News
        
        Args:
            html_content: HTML content from Google News page
            
        Returns:
            List of news articles
        """
        articles = []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            article_containers = soup.select("article")
            
            for idx, article_elem in enumerate(article_containers[:self.max_results]):
                try:
                    headline_elem = article_elem.select_one("h3 a")
                    if not headline_elem:
                        continue
                    
                    title = headline_elem.get_text(strip=True)
                    
                    url = headline_elem.get("href", "")
                    if url and url.startswith("./articles"):
                        url = f"https://news.google.com{url[1:]}"
                    
                    source_elem = article_elem.select_one("div[data-source]")
                    source = source_elem.get_text(strip=True) if source_elem else ""
                    
                    time_elem = article_elem.select_one("time")
                    date_str = time_elem.get("datetime", "") if time_elem else ""
                    publish_date = self._normalize_date(date_str)
                    
                    summary_elem = article_elem.select_one("p")
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    if title and url:
                        article = self._create_article(
                            title=title,
                            url=url,
                            content=summary,
                            summary=summary,
                            publish_date=publish_date,
                            author=source,
                            tags=["news", "google_news", self.query.lower()]
                        )
                        articles.append(article)
                        self.logger.debug(f"Extracted article: {title}")
                
                except Exception as e:
                    self.logger.warning(f"Error extracting article: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(articles)} news articles")
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {str(e)}")
        
        return articles
