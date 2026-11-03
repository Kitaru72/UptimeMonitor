import asyncio

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitor import MonitorModel
from app.models.check import CheckModel
from app.services.checker import check_url


async def check_urls(urls: list[str], semaphore: asyncio.Semaphore) -> list[dict]:
    async def check_url_with_limit(url):
        async with semaphore:
            return await check_url(url)

    coroutines = [check_url_with_limit(url) for url in urls]

    results = await asyncio.gather(*coroutines)
    return results


async def run_active_monitors_checks(db: AsyncSession) -> list[CheckModel]:
    sem = asyncio.Semaphore(10)

    statement = (
        select(MonitorModel)
        .where(MonitorModel.is_active.is_(True))
        .order_by(MonitorModel.id)
    )
    result = await db.scalars(statement)
    monitors = result.all()

    urls = [monitor.url for monitor in monitors]
    responses = await check_urls(urls, sem)

    current_time = datetime.now(timezone.utc)

    checks = []
    for monitor, check_result in zip(monitors, responses):
        new_check = CheckModel(
            monitor_id=monitor.id,
            status=check_result["status"],
            http_status_code=check_result["http_status_code"],
            error_type=check_result["error_type"],
            duration_ms=check_result["duration_ms"],
            checked_at=current_time,
        )
        monitor.last_checked_at = new_check.checked_at

        db.add(new_check)
        checks.append(new_check)

    await db.commit()
    return checks
