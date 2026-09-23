from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.schemas.check import Check
from app.services.batch_checker import run_active_monitors_checks

router = APIRouter(prefix="/checks", tags=["checks"])


@router.post("/run", response_model=list[Check])
async def run_checks(db: AsyncSession = Depends(get_async_db)):
    return await run_active_monitors_checks(db)
