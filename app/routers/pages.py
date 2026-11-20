from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitor import MonitorModel
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