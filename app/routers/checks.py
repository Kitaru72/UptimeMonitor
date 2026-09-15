from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.check import CheckModel
from app.models.monitor import MonitorModel
from app.schemas.check import Check
from app.services.checker import check_url


router = APIRouter(
    prefix="/monitors/{monitor_id}/checks",
    tags=["checks"],
)


@router.get(
    "",
    response_model=list[Check],
)
def get_checks(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )

    statement = (
        select(CheckModel)
        .where(CheckModel.monitor_id == monitor_id)
        .order_by(CheckModel.id)
    )

    result = db.scalars(statement)
    return result.all()


@router.post(
    "",
    response_model=Check,
    status_code=201,
)
def create_check(monitor_id: int, db: Session = Depends(get_db)):
    monitor = db.get(MonitorModel, monitor_id)

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Monitor not found",
        )
    if not monitor.is_active:
        monitor.is_active = True

    check_result = check_url(monitor.url)

    new_check = CheckModel(
        monitor_id=monitor_id,
        status=check_result["status"],
        http_status_code=check_result["http_status_code"],
        error_type=check_result["error_type"],
        duration_ms=check_result["duration_ms"],
        checked_at=datetime.now().astimezone(),
    )

    monitor.last_checked_at = new_check.checked_at

    db.add(new_check)
    db.commit()
    db.refresh(new_check)

    return new_check
