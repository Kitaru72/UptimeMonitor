from datetime import datetime
from pydantic import BaseModel, HttpUrl

class MonitorCreate(BaseModel):
    url: HttpUrl


class Monitor(BaseModel):
    id: int
    url: HttpUrl
    created_at: datetime