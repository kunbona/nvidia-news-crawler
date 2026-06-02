"""
NVIDIA GTC (GPU Technology Conference) crawler
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class GTCCrawler(BaseCrawler):
    """Crawler for NVIDIA GTC content"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("gtc", config)
    
    async def extract_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract GTC session information
        
        Args:
            html_content: HTML content from GTC page
            
        Returns:
            List of GTC sessions
        """
        sessions = []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            selectors = self.config.get("selectors", {})
            session_container = selectors.get("article_container", ".gtc-session")
            
            for session_elem in soup.select(session_container):
                try:
                    title_elem = session_elem.select_one(selectors.get("title", ".session-title"))
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    url_elem = session_elem.select_one(selectors.get("url", ".session-link"))
                    url = url_elem.get("href", "") if url_elem else ""
                    
                    if url and not url.startswith("http"):
                        url = "https://www.nvidia.com" + url
                    
                    date_elem = session_elem.select_one(selectors.get("date", ".session-date"))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    publish_date = self._normalize_date(date_str)
                    
                    desc_elem = session_elem.select_one(".session-description")
                    content = desc_elem.get_text(strip=True) if desc_elem else ""
                    summary = content[:200] + "..." if len(content) > 200 else content
                    
                    speaker_elems = session_elem.select(".session-speaker")
                    speakers = [speaker.get_text(strip=True) for speaker in speaker_elems]
                    author = ", ".join(speakers) if speakers else ""
                    
                    if title and url:
                        article = self._create_article(
                            title=title,
                            url=url,
                            content=content,
                            summary=summary,
                            publish_date=publish_date,
                            author=author,
                            tags=["gtc", "conference", "gpu"]
                        )
                        sessions.append(article)
                        self.logger.debug(f"Extracted GTC session: {title}")
                
                except Exception as e:
                    self.logger.warning(f"Error extracting session: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(sessions)} GTC sessions")
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {str(e)}")
        
        return sessions
