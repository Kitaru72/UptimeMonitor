from app.services.batch_checker import run_active_monitors_checks
from app.database import AsyncSessionLocal


async def run_scheduled_monitor_checks() -> None:
    async with AsyncSessionLocal() as db:
        await run_active_monitors_checks(db)
