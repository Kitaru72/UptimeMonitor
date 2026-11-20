from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from app.scheduler import create_scheduler
from app.routers.monitors import router as monitors_router
from app.routers.checks import router as check_router
from app.routers.batch_checks import router as batch_check_router
from app.routers.service import router as service_router
from app.routers.pages import router as pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = create_scheduler()
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()

enable_api_docs = os.getenv("ENABLE_API_DOCS", "false").strip().lower() == "true"

docs_url, redoc_url, openapi_url = (
    ("/docs", "/redoc", "/openapi.json")
    if enable_api_docs
    else (None, None, None)
)

app = FastAPI(
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url
)

app.include_router(monitors_router)
app.include_router(check_router)
app.include_router(batch_check_router)
app.include_router(service_router)
app.include_router(pages_router)