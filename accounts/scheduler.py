"""
Background scheduler for updating occupancy data from Waitz.io
"""
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def fetch_waitz_occupancy():
    """
    Scheduled task to fetch occupancy data from Waitz.io
    Runs every 10 minutes
    """
    try:
        logger.info(f"[{timezone.now()}] Starting scheduled Waitz occupancy update...")
        
        # Call the management command to fetch occupancy data
        # This will update all buildings that have waitz_id set
        call_command('fetch_waitz_occupancy', '--all')
        
        logger.info(f"[{timezone.now()}] Scheduled Waitz occupancy update completed")
    except Exception as e:
        logger.error(f"[{timezone.now()}] Error in scheduled Waitz update: {str(e)}")


def start_scheduler():
    """
    Start the background scheduler
    """
    scheduler = BackgroundScheduler()
    
    # Schedule the job to run every 10 minutes
    scheduler.add_job(
        fetch_waitz_occupancy,
        'interval',
        minutes=10,
        id='fetch_waitz_occupancy',
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )
    
    # Run immediately on startup (optional)
    # scheduler.add_job(
    #     fetch_waitz_occupancy,
    #     'date',
    #     run_date=timezone.now(),
    #     id='fetch_waitz_occupancy_startup'
    # )
    
    scheduler.start()
    logger.info("Waitz occupancy scheduler started - will update every 10 minutes")
    
    return scheduler

