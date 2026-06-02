"""
Task scheduler for automated crawling
"""
from datetime import datetime
from typing import Dict, Any, Callable
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger


class TaskScheduler:
    """Manage scheduled crawling tasks"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
    
    def schedule_job(
        self,
        job_id: str,
        job_func: Callable,
        cron_expression: str,
        job_args: tuple = (),
        job_kwargs: Dict[str, Any] = None
    ) -> bool:
        """
        Schedule a job using cron expression
        
        Args:
            job_id: Unique job ID
            job_func: Function to execute
            cron_expression: Cron expression
            job_args: Function arguments
            job_kwargs: Function keyword arguments
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if job_kwargs is None:
                job_kwargs = {}
            
            parts = cron_expression.split()
            if len(parts) != 5:
                logger.error(f"Invalid cron expression: {cron_expression}")
                return False
            
            minute, hour, day, month, day_of_week = parts
            
            job = self.scheduler.add_job(
                job_func,
                'cron',
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                args=job_args,
                kwargs=job_kwargs,
                id=job_id,
                name=job_id,
                replace_existing=True,
            )
            
            self.jobs[job_id] = job
            logger.info(f"Scheduled job: {job_id} with cron '{cron_expression}'")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling job {job_id}: {str(e)}")
            return False
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def get_jobs(self) -> Dict[str, Any]:
        """Get all scheduled jobs"""
        return self.jobs
