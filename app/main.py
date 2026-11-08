from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.scheduler import create_scheduler
from app.routers.monitors import router as monitors_router
from app.routers.checks import router as check_router
from app.routers.batch_checks import router as batch_check_router
from app.routers.service import router as service_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(monitors_router)
app.include_router(check_router)
app.include_router(batch_check_router)
app.include_router(service_router)
