from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Query

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.check import CheckModel
from app.models.monitor import MonitorModel
from app.schemas.check import Check
from app.schemas.pagination import PaginatedResponse
from app.services.checker import check_url


router = APIRouter(
    prefix="/monitors/{monitor_id}/checks",
    tags=["checks"],
)


@router.get(
    "",
    response_model=PaginatedResponse[Check],
)
async def get_checks(
    monitor_id: int,
    db: AsyncSession = Depends(get_async_db),
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0
):
    monitor = await db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    count_statement = select(func.count()).select_from(CheckModel).where(CheckModel.monitor_id == monitor_id)
    total = await db.scalar(count_statement)

    statement = (
        select(CheckModel)
        .where(CheckModel.monitor_id == monitor_id)
        .order_by(CheckModel.checked_at.desc(), CheckModel.id.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.scalars(statement)
    checks = result.all()

    return {
        "items": checks,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post(
    "",
    response_model=Check,
    status_code=201,
)
async def create_check(monitor_id: int, db: AsyncSession = Depends(get_async_db)):
    monitor = await db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )
    if not monitor.is_active:
        monitor.is_active = True

    check_result = await check_url(monitor.url)

    new_check = CheckModel(
        monitor_id=monitor_id,
        status=check_result["status"],
        http_status_code=check_result["http_status_code"],
        error_type=check_result["error_type"],
        duration_ms=check_result["duration_ms"],
        checked_at=datetime.now(timezone.utc),
    )

    monitor.last_checked_at = new_check.checked_at

    db.add(new_check)
    await db.commit()
    await db.refresh(new_check)

    return new_check
