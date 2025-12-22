"""Periodic price sync scheduler for maintaining current cloud pricing data.

This module provides scheduling functionality to automatically sync cloud instance
prices from AWS public offerings at regular intervals (default: daily at 2 AM UTC).

Usage in Flask app:
    from utils.price_sync_scheduler import start_scheduler, stop_scheduler
    
    app = Flask(__name__)
    start_scheduler(app)
    
    @app.teardown_appcontext
    def shutdown(exception=None):
        stop_scheduler()
"""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
scheduler = None


def sync_aws_prices():
    """Execute AWS price sync job.
    
    Syncs public EC2 offerings without requiring AWS credentials.
    Catches and logs any errors to avoid crashing the scheduler.
    """
    try:
        from utils.aws_price_sync import sync_prices_public

        logger.info(f"[{datetime.now()}] Starting AWS price sync job...")
        sync_prices_public(write_back=True, location="us-east-1")
        logger.info(f"[{datetime.now()}] AWS price sync completed successfully.")
    except Exception as e:
        logger.error(f"[{datetime.now()}] AWS price sync failed: {e}", exc_info=True)


def start_scheduler(app=None, cron_hour=2, cron_minute=0):
    """Start the background scheduler for periodic price syncs.
    
    Args:
        app: Flask app instance (optional; used for app context if needed).
        cron_hour: Hour of day (0-23) to run sync (default: 2 = 2 AM UTC).
        cron_minute: Minute of hour (0-59) to run sync (default: 0).
    """
    global scheduler

    if scheduler and scheduler.running:
        logger.warning("Scheduler is already running.")
        return

    scheduler = BackgroundScheduler()

    # Schedule AWS price sync to run daily at specified time (UTC)
    scheduler.add_job(
        sync_aws_prices,
        trigger=CronTrigger(hour=cron_hour, minute=cron_minute),
        id="aws_price_sync",
        name="AWS Price Sync",
        replace_existing=True,
        misfire_grace_time=60,  # Allow up to 60s grace for missed runs
    )

    scheduler.start()
    logger.info(
        f"Scheduler started. AWS price sync scheduled daily at {cron_hour:02d}:{cron_minute:02d} UTC."
    )


def stop_scheduler():
    """Stop the background scheduler gracefully."""
    global scheduler

    if scheduler and scheduler.running:
        scheduler.shutdown(wait=True)
        scheduler = None
        logger.info("Scheduler stopped.")


def is_scheduler_running():
    """Check if scheduler is currently running."""
    global scheduler
    return scheduler is not None and scheduler.running
