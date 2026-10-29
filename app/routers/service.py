from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db

router = APIRouter(
    tags=["service"]
)

@router.get(
    "/ready",
    status_code=status.HTTP_200_OK
)
async def get_database_status(
    db: AsyncSession = Depends(get_async_db)
):
    try:
        await db.scalar(select(1))
        return {"status": "ready"}
    except (DBAPIError, OSError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable"}
        )
