"""
Database models using SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class Article(Base):
    """Article model"""
    __tablename__ = "articles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=False, unique=True)
    source = Column(String(100), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    author = Column(String(200))
    tags = Column(JSON, default=[])
    keywords = Column(JSON, default=[])
    publish_date = Column(DateTime)
    crawled_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metrics = Column(JSON)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "content": self.content,
            "summary": self.summary,
            "author": self.author,
            "tags": self.tags,
            "keywords": self.keywords,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "crawled_at": self.crawled_at.isoformat() if self.crawled_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metrics": self.metrics,
        }


class FinancialReport(Base):
    """Financial report model"""
    __tablename__ = "financial_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    url = Column(String(2000), nullable=False, unique=True)
    report_date = Column(DateTime)
    quarter = Column(String(20))
    document_url = Column(String(2000))
    extracted_text = Column(Text)
    summary = Column(Text)
    tags = Column(JSON, default=[])
    crawled_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "quarter": self.quarter,
            "document_url": self.document_url,
            "extracted_text": self.extracted_text,
            "summary": self.summary,
            "tags": self.tags,
            "crawled_at": self.crawled_at.isoformat() if self.crawled_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CrawlLog(Base):
    """Crawl execution log"""
    __tablename__ = "crawl_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crawler_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    articles_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "crawler_name": self.crawler_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "articles_count": self.articles_count,
            "error_message": self.error_message,
        }
