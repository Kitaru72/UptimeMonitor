from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.monitor import MonitorModel
from app.schemas.monitor import Monitor, MonitorCreate

router = APIRouter(
    prefix="/monitors",
    tags=["monitors"],
)


# GET ALL MONITORS
@router.get(
    "",
    response_model=list[Monitor],
)
async def get_monitors(db: AsyncSession = Depends(get_async_db)):
    statement = select(MonitorModel)
    result = await db.scalars(statement)
    return result.all()


# GET ONE MONITOR VIA ID
@router.get(
    "/{monitor_id}",
    response_model=Monitor,
)
async def get_monitor(monitor_id: int, db: AsyncSession = Depends(get_async_db)):
    monitor = await db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    return monitor


# CREATE MONITOR
@router.post(
    "",
    response_model=Monitor,
    status_code=201,
)
async def create_monitor(
    monitor_data: MonitorCreate,
    response: Response,
    db: AsyncSession = Depends(get_async_db),
):
    statement = select(MonitorModel).where(MonitorModel.url == str(monitor_data.url))
    existing_monitor = await db.scalar(statement)
    if existing_monitor is None:
        new_monitor = MonitorModel(
            url=str(monitor_data.url),
            created_at=datetime.now(timezone.utc)
        )

        db.add(new_monitor)
        await db.commit()
        await db.refresh(new_monitor)

        return new_monitor

    else:
        response.status_code = 200
        return existing_monitor


# DELETE MONITOR
@router.delete(
    "/{monitor_id}",
    status_code=204,
)
async def delete_monitor(monitor_id: int, db: AsyncSession = Depends(get_async_db)):
    monitor = await db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    await db.delete(monitor)
    await db.commit()
    return


@router.post(
    "/{monitor_id}/pause",
    status_code=200,
    response_model=Monitor,
)
async def pause_monitor(monitor_id: int, db: AsyncSession = Depends(get_async_db)):
    monitor = await db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    monitor.is_active = False

    await db.commit()
    await db.refresh(monitor)

    return monitor


@router.post(
    "/{monitor_id}/resume",
    status_code=200,
    response_model=Monitor,
)
async def resume_monitor(monitor_id: int, db: AsyncSession = Depends(get_async_db)):
    monitor = await db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    monitor.is_active = True

    await db.commit()
    await db.refresh(monitor)

    return monitor
