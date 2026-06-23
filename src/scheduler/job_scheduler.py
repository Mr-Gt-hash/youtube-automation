"""
Job Scheduler — runs the full pipeline on a cron schedule using APScheduler.
Run as a daemon: python -m src.scheduler.job_scheduler
"""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from config.settings import Settings
from main import run_pipeline

logger = logging.getLogger(__name__)


def scheduled_pipeline():
    logger.info("⏰ Scheduler triggered: starting pipeline run")
    run_pipeline()


def scheduled_analytics():
    from src.analytics.tracker import AnalyticsTracker
    cfg = Settings()
    tracker = AnalyticsTracker(cfg)
    tracker.run()


if __name__ == "__main__":
    cfg = Settings()
    scheduler = BlockingScheduler(timezone="UTC")

    # Full pipeline daily at 09:00 UTC
    scheduler.add_job(
        scheduled_pipeline,
        CronTrigger(hour=9, minute=0),
        id="daily_pipeline",
        name="Daily YouTube Pipeline",
        misfire_grace_time=3600,
    )

    # Analytics every 6 hours
    scheduler.add_job(
        scheduled_analytics,
        CronTrigger(hour="*/6"),
        id="analytics",
        name="Analytics Monitor",
    )

    logger.info("🕒 Scheduler started. Jobs: daily_pipeline @ 09:00 UTC, analytics every 6h")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
