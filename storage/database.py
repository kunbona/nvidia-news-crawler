"""
Database connection and operations
"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Session
from sqlalchemy.orm import sessionmaker
from loguru import logger
from .models import Base, Article, FinancialReport, CrawlLog


class Database:
    """Database manager"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize database connection
        
        Args:
            db_config: Database configuration dictionary
        """
        self.db_type = db_config.get("type", "postgresql")
        self.config = db_config
        self.engine = None
        self.Session = None
        
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        try:
            if self.db_type == "postgresql":
                connection_string = self._build_postgres_connection_string()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            self.engine = create_engine(connection_string, echo=self.config.get("echo_sql", False))
            self.Session = sessionmaker(bind=self.engine)
            
            Base.metadata.create_all(self.engine)
            logger.info(f"Connected to {self.db_type} database")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def _build_postgres_connection_string(self) -> str:
        """Build PostgreSQL connection string"""
        user = self.config.get("user") or os.getenv("DB_USER")
        password = self.config.get("password") or os.getenv("DB_PASSWORD")
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 5432)
        database = self.config.get("name") or os.getenv("DB_NAME")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.Session()
    
    def save_article(self, article_data: Dict[str, Any]) -> Optional[Article]:
        """
        Save article to database
        
        Args:
            article_data: Article data dictionary
            
        Returns:
            Saved Article object or None
        """
        session = self.get_session()
        
        try:
            existing = session.query(Article).filter_by(url=article_data["url"]).first()
            if existing:
                logger.debug(f"Article already exists: {article_data['url']}")
                session.close()
                return existing
            
            article = Article(
                title=article_data.get("title"),
                url=article_data.get("url"),
                source=article_data.get("source", "unknown"),
                content=article_data.get("content", ""),
                summary=article_data.get("summary", ""),
                author=article_data.get("author", ""),
                tags=article_data.get("tags", []),
                keywords=article_data.get("keywords", []),
                publish_date=article_data.get("publish_date"),
                metrics=article_data.get("metrics"),
            )
            
            session.add(article)
            session.commit()
            logger.info(f"Saved article: {article.title}")
            session.close()
            return article
            
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}")
            session.rollback()
            session.close()
            return None
    
    def save_articles(self, articles: List[Dict[str, Any]]) -> int:
        """
        Save multiple articles
        
        Args:
            articles: List of article data dictionaries
            
        Returns:
            Number of articles saved
        """
        saved_count = 0
        for article_data in articles:
            if self.save_article(article_data):
                saved_count += 1
        
        return saved_count
    
    def get_articles_by_source(self, source: str, limit: int = 100) -> List[Article]:
        """
        Get articles by source
        
        Args:
            source: Source name
            limit: Maximum number of articles
            
        Returns:
            List of Article objects
        """
        session = self.get_session()
        
        try:
            articles = session.query(Article).filter_by(source=source).order_by(
                Article.publish_date.desc()
            ).limit(limit).all()
            
            session.close()
            return articles
        except Exception as e:
            logger.error(f"Error querying articles: {str(e)}")
            session.close()
            return []
    
    def save_crawl_log(
        self,
        crawler_name: str,
        status: str,
        start_time: datetime,
        articles_count: int = 0,
        error_message: str = ""
    ) -> Optional[CrawlLog]:
        """
        Save crawl execution log
        
        Args:
            crawler_name: Crawler name
            status: Execution status
            start_time: Start time
            articles_count: Number of articles crawled
            error_message: Error message if any
            
        Returns:
            Saved CrawlLog object or None
        """
        session = self.get_session()
        
        try:
            log = CrawlLog(
                crawler_name=crawler_name,
                status=status,
                start_time=start_time,
                end_time=datetime.utcnow(),
                articles_count=articles_count,
                error_message=error_message,
            )
            
            session.add(log)
            session.commit()
            logger.info(f"Saved crawl log for {crawler_name}: {status}")
            session.close()
            return log
            
        except Exception as e:
            logger.error(f"Error saving crawl log: {str(e)}")
            session.rollback()
            session.close()
            return None
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
