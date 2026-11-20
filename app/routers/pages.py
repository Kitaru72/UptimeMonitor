from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitor import MonitorModel
from app.models.check import CheckModel
from app.database import get_async_db


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(
    tags=["HTML"]
)

@router.get(
    "/",
    response_class=HTMLResponse
)
async def get_html_header(
    incoming_request: Request,
    db: AsyncSession = Depends(get_async_db),
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    statement = (
        select(MonitorModel)
        .order_by(MonitorModel.id)
        .limit(limit)
    )

    result = await db.scalars(statement)
    monitors = result.all()

    return templates.TemplateResponse(
        request=incoming_request,
        name="index.html",
        context={
            "title": "UptimeMonitor",
            "monitors": monitors
        },
        
    )


@router.get(
    "/monitors/{monitor_id}/history",
    response_class=HTMLResponse
)
async def get_monitor_history(
    incoming_request: Request,
    monitor_id: int,
    db: AsyncSession = Depends(get_async_db),
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    monitor = await db.scalar(
        select(MonitorModel)
        .where(MonitorModel.id == monitor_id)
        )

    if monitor is None:
        raise HTTPException(
            status_code=404,
            detail="Монитор не найден",
        )

    monitor_url = monitor.url

    stmt = (
        select(CheckModel)
        .where(CheckModel.monitor_id == monitor_id)
        .order_by(CheckModel.checked_at.desc(), CheckModel.id.desc())
        .limit(limit)
    )

    result = await db.scalars(stmt)
    checks = result.all()

    return templates.TemplateResponse(
        request=incoming_request,
        name="history.html",
        context={
            "title": f"История проверок {monitor_url}",
            "checks": checks,
        }
    )
