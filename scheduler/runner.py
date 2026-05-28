from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from config import get_settings
from scheduler.jobs import AutomationJobs


def build_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    jobs = AutomationJobs()
    scheduler = AsyncIOScheduler(timezone=settings.timezone)
    if settings.run_scan_on_startup:
        first_run = datetime.now() + timedelta(seconds=5)
        scheduler.add_job(jobs.scan_and_publish, DateTrigger(run_date=first_run), id="startup-scan", replace_existing=True)
        scheduler.add_job(jobs.check_toss_results, DateTrigger(run_date=first_run + timedelta(seconds=20)), id="startup-results-check", replace_existing=True)
    scheduler.add_job(jobs.scan_and_publish, IntervalTrigger(minutes=settings.posting_interval_minutes), id="scan-and-publish", replace_existing=True)
    scheduler.add_job(jobs.check_toss_results, IntervalTrigger(minutes=10), id="check-toss-results", replace_existing=True)
    scheduler.add_job(jobs.delete_outdated_posts, IntervalTrigger(hours=1), id="delete-outdated-posts", replace_existing=True)
    scheduler.add_job(jobs.post_daily_schedule, CronTrigger(hour=8, minute=0), id="daily-schedule", replace_existing=True)
    scheduler.add_job(jobs.post_engagement, CronTrigger(hour=14, minute=0), id="engagement", replace_existing=True)
    scheduler.add_job(jobs.post_vip_teaser, CronTrigger(hour=20, minute=0), id="vip-teaser", replace_existing=True)
    return scheduler
