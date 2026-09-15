from datetime import datetime
from pydantic import BaseModel, HttpUrl

class MonitorCreate(BaseModel):
    url: HttpUrl


class Monitor(BaseModel):
    id: int
    url: HttpUrl
    created_at: datetime
    is_active: bool
    last_checked_at: datetime | None = None
