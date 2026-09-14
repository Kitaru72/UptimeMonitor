from datetime import datetime

from fastapi import APIRouter, HTTPException, Response, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
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
def get_monitors(db: Session = Depends(get_db)):
    statement = select(MonitorModel)
    result = db.scalars(statement)
    return result.all()


# GET ONE MONITOR VIA ID
@router.get(
    "/{monitor_id}",
    response_model=Monitor,
)
def get_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(MonitorModel, monitor_id)

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
def create_monitor(monitor_data: MonitorCreate, response: Response, db: Session = Depends(get_db)):
    statement = select(MonitorModel).where(
        MonitorModel.url == str(monitor_data.url)
    )
    existing_monitor = db.scalar(statement)
    if existing_monitor is None:
        new_monitor = MonitorModel(
            url=str(monitor_data.url),
            created_at=datetime.now().astimezone()
        )

        db.add(new_monitor)
        db.commit()
        db.refresh(new_monitor)

        return new_monitor

    else:
        response.status_code = 200
        return existing_monitor


# DELETE MONITOR
@router.delete(
    "/{monitor_id}",
    status_code=204,
)
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    db.delete(monitor)
    db.commit()
    return


@router.post(
    "/{monitor_id}/pause",
    status_code=200,
    response_model=Monitor,
)
def pause_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    monitor.is_active = False

    db.commit()
    db.refresh(monitor)

    return monitor


@router.post(
    "/{monitor_id}/resume",
    status_code=200,
    response_model=Monitor,
)
def resume_monitor(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    monitor.is_active = True

    db.commit()
    db.refresh(monitor)

    return monitor
