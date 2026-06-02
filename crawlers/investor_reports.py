"""
NVIDIA investor relations and financial reports crawler
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from .base_crawler import BaseCrawler


class InvestorReportsCrawler(BaseCrawler):
    """Crawler for NVIDIA financial reports and investor relations"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("investor_reports", config)
    
    async def extract_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract financial reports and investor information
        
        Args:
            html_content: HTML content from investor relations page
            
        Returns:
            List of reports
        """
        reports = []
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            selectors = self.config.get("selectors", {})
            report_container = selectors.get("report_container", ".report-item")
            
            for report_elem in soup.select(report_container):
                try:
                    title_elem = report_elem.select_one(selectors.get("title", ".report-title"))
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    
                    url_elem = report_elem.select_one(selectors.get("url", ".report-link"))
                    url = url_elem.get("href", "") if url_elem else ""
                    
                    if url and not url.startswith("http"):
                        url = "https://investor.nvidia.com" + url
                    
                    date_elem = report_elem.select_one(selectors.get("date", ".report-date"))
                    date_str = date_elem.get_text(strip=True) if date_elem else ""
                    publish_date = self._normalize_date(date_str)
                    
                    type_elem = report_elem.select_one(".report-type")
                    report_type = type_elem.get_text(strip=True) if type_elem else ""
                    
                    content = report_elem.get_text(strip=True)
                    summary = content[:200] + "..." if len(content) > 200 else content
                    
                    if title and url:
                        article = self._create_article(
                            title=title,
                            url=url,
                            content=content,
                            summary=summary,
                            publish_date=publish_date,
                            tags=["investor", "financial", "report", report_type.lower() if report_type else "document"]
                        )
                        reports.append(article)
                        self.logger.debug(f"Extracted report: {title}")
                
                except Exception as e:
                    self.logger.warning(f"Error extracting report: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(reports)} financial reports")
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {str(e)}")
        
        return reports
