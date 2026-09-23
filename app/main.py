from fastapi import FastAPI

from app.routers.monitors import router as monitors_router
from app.routers.checks import router as check_router
from app.routers.batch_checks import router as batch_check_router


app = FastAPI()
app.include_router(monitors_router)
app.include_router(check_router)
app.include_router(batch_check_router)