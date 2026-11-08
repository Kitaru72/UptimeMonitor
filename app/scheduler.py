import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.jobs.monitor_checks import run_scheduled_monitor_checks


def create_scheduler() -> AsyncIOScheduler:
    cron_expression = os.getenv("CHECK_SCHEDULE_CRON", "*/3 * * * *")

    scheduler = AsyncIOScheduler(timezone="UTC")

    trigger = CronTrigger.from_crontab(cron_expression, timezone="UTC")

    scheduler.add_job(
        run_scheduled_monitor_checks,
        trigger=trigger,
        id="run-monitor-checks",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
        misfire_grace_time=60,
    )

    return scheduler
