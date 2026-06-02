"""
Main entry point with file export support
"""
import asyncio
from datetime import datetime
from pathlib import Path
import sys

from utils.logger import setup_logger
from utils.helpers import load_config, save_json, load_json
from crawlers import (
    NvidiaOfficialCrawler,
    GTCCrawler,
    InvestorReportsCrawler,
    GoogleNewsCrawler,
    TwitterCrawler,
)
from extractors.data_cleaner import DataCleaner
from storage.database import Database
from storage.file_exporter_impl import FileExporter
from scheduler.task_scheduler import TaskScheduler
from loguru import logger


class CrawlerManager:
    """Manage all crawlers and their execution"""
    
    def __init__(self, config_file: str = "config/config.yaml"):
        """
        Initialize crawler manager
        
        Args:
            config_file: Configuration file path
        """
        # Load configuration
        self.config = load_config(config_file)
        
        # Setup logging
        log_config = self.config.get("logging", {})
        setup_logger(
            log_level=log_config.get("level", "INFO"),
            log_file=log_config.get("file", "logs/crawler.log")
        )
        
        # Initialize database
        db_config = self.config.get("database", {})
        self.db = Database(db_config)
        
        # Initialize file exporter
        storage_config = self.config.get("storage", {})
        self.exporter = FileExporter(output_dir=storage_config.get("archive_path", "./output"))
        
        # Initialize cleaner
        self.cleaner = DataCleaner()
        
        # Initialize scheduler
        self.scheduler = TaskScheduler()
        
        # Initialize crawlers
        self.crawlers = {}
        self._initialize_crawlers()
        
        logger.info("Crawler manager initialized")
    
    def _initialize_crawlers(self):
        """Initialize all crawlers"""
        crawlers_config = self.config.get("crawlers", {})
        
        # NVIDIA Official
        if crawlers_config.get("nvidia_official", {}).get("enabled", False):
            self.crawlers["nvidia_official"] = NvidiaOfficialCrawler(
                crawlers_config["nvidia_official"]
            )
        
        # GTC
        if crawlers_config.get("gtc", {}).get("enabled", False):
            self.crawlers["gtc"] = GTCCrawler(crawlers_config["gtc"])
        
        # Investor Reports
        if crawlers_config.get("investor_reports", {}).get("enabled", False):
            self.crawlers["investor_reports"] = InvestorReportsCrawler(
                crawlers_config["investor_reports"]
            )
        
        # Google News
        if crawlers_config.get("google_news", {}).get("enabled", False):
            self.crawlers["google_news"] = GoogleNewsCrawler(
                crawlers_config["google_news"]
            )
        
        # Twitter
        if crawlers_config.get("twitter", {}).get("enabled", False):
            self.crawlers["twitter"] = TwitterCrawler(crawlers_config["twitter"])
        
        logger.info(f"Initialized {len(self.crawlers)} crawlers")
    
    async def run_crawler(self, crawler_name: str, export_format: str = None) -> int:
        """
        Run a single crawler
        
        Args:
            crawler_name: Name of crawler to run
            export_format: Export format (json, csv, excel, markdown, or None for no export)
            
        Returns:
            Number of articles saved
        """
        if crawler_name not in self.crawlers:
            logger.error(f"Crawler not found: {crawler_name}")
            return 0
        
        crawler = self.crawlers[crawler_name]
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Running crawler: {crawler_name}")
            
            # Run crawler
            articles = await crawler.async_crawl()
            logger.info(f"Crawler returned {len(articles)} articles")
            
            # Clean articles
            cleaned_articles = self.cleaner.clean_articles(articles)
            logger.info(f"After cleaning: {len(cleaned_articles)} articles")
            
            # Save to database
            saved_count = self.db.save_articles(cleaned_articles)
            
            # Export to file if format specified
            if export_format and cleaned_articles:
                self._export_articles(cleaned_articles, export_format, crawler_name)
            
            # Save crawl log
            self.db.save_crawl_log(
                crawler_name=crawler_name,
                status="success",
                start_time=start_time,
                articles_count=saved_count,
            )
            
            logger.info(f"Crawler {crawler_name} completed: {saved_count} articles saved")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error running crawler {crawler_name}: {str(e)}")
            self.db.save_crawl_log(
                crawler_name=crawler_name,
                status="failed",
                start_time=start_time,
                error_message=str(e),
            )
            return 0
    
    async def run_all_crawlers(self, export_format: str = None) -> int:
        """
        Run all crawlers
        
        Args:
            export_format: Export format (json, csv, excel, markdown, or None for no export)
            
        Returns:
            Total number of articles saved
        """
        total_saved = 0
        
        for crawler_name in self.crawlers:
            saved = await self.run_crawler(crawler_name, export_format)
            total_saved += saved
        
        return total_saved
    
    def _export_articles(self, articles: list, format: str, source_name: str = None) -> bool:
        """
        Export articles to file
        
        Args:
            articles: List of articles to export
            format: Export format (json, csv, excel, markdown)
            source_name: Source name for filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = source_name if source_name else "articles"
            
            if format == "json":
                filename = f"{prefix}_{timestamp}.json"
                return self.exporter.export_json(articles, filename)
            elif format == "csv":
                filename = f"{prefix}_{timestamp}.csv"
                return self.exporter.export_csv(articles, filename)
            elif format == "excel":
                filename = f"{prefix}_{timestamp}.xlsx"
                return self.exporter.export_excel(articles, filename)
            elif format == "markdown":
                filename = f"{prefix}_{timestamp}.md"
                return self.exporter.export_markdown(articles, filename)
            else:
                logger.warning(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            logger.error(f"Error exporting articles: {str(e)}")
            return False
    
    def schedule_crawlers(self):
        """Schedule all crawlers"""
        crawlers_config = self.config.get("crawlers", {})
        
        for crawler_name, crawler in self.crawlers.items():
            config = crawlers_config.get(crawler_name, {})
            schedule = config.get("schedule")
            
            if schedule:
                self.scheduler.schedule_job(
                    job_id=f"crawler_{crawler_name}",
                    job_func=self.run_crawler,
                    cron_expression=schedule,
                    job_args=(crawler_name,)
                )
                logger.info(f"Scheduled {crawler_name} with cron: {schedule}")
    
    def start(self, schedule: bool = True, export_format: str = None):
        """
        Start crawler manager
        
        Args:
            schedule: Whether to schedule crawlers
            export_format: Export format for crawled data
        """
        if schedule:
            self.schedule_crawlers()
            self.scheduler.start()
            logger.info("Scheduler started. Press Ctrl+C to stop.")
            
            # Keep running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping scheduler...")
                self.scheduler.stop()
        else:
            # Run crawlers once
            asyncio.run(self.run_all_crawlers(export_format))
    
    def stop(self):
        """Stop crawler manager"""
        self.scheduler.stop()
        self.db.close()
        logger.info("Crawler manager stopped")
    
    def export_all_to_formats(self, crawler_name: str = None) -> bool:
        """
        Export data to all formats
        
        Args:
            crawler_name: Specific crawler to export (or None for all)
            
        Returns:
            True if successful
        """
        try:
            if crawler_name:
                # Export specific crawler's data
                articles = self.db.get_articles_by_source(crawler_name)
                if articles:
                    articles_data = [a.to_dict() for a in articles]
                    return self.exporter.export_all_formats(articles_data)
            else:
                # Export all data
                logger.info("Exporting all crawled data...")
                # This would require fetching all articles
                logger.warning("Export all formats feature requires database query")
                return False
        except Exception as e:
            logger.error(f"Error exporting to all formats: {str(e)}")
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NVIDIA News Crawler")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "--crawler",
        type=str,
        help="Run specific crawler (e.g., nvidia_official, gtc)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run crawlers once without scheduling"
    )
    parser.add_argument(
        "--export",
        type=str,
        choices=["json", "csv", "excel", "markdown"],
        help="Export format for crawled data"
    )
    parser.add_argument(
        "--export-all",
        action="store_true",
        help="Export to all formats"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize crawler manager
    manager = CrawlerManager(args.config)
    
    try:
        if args.crawler:
            # Run specific crawler
            asyncio.run(manager.run_crawler(args.crawler, args.export))
        elif args.once:
            # Run all crawlers once
            asyncio.run(manager.run_all_crawlers(args.export))
        elif args.export_all:
            # Export all data to all formats
            manager.export_all_to_formats()
        else:
            # Start scheduler
            manager.start(schedule=True, export_format=args.export)
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        manager.stop()


if __name__ == "__main__":
    main()
