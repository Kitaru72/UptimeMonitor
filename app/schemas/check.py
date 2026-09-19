from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Check(BaseModel):
    id: int
    monitor_id: int
    status: Literal["UP", "DOWN"]
    http_status_code: int | None = None
    error_type: (
        Literal["TIMEOUT", "DNS_ERROR", "CONNECTION_ERROR", "REQUEST_ERROR"] | None
    ) = None
    duration_ms: int
    checked_at: datetime
