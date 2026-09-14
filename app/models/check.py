from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CheckModel(Base):
    __tablename__ = "checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    monitor_id: Mapped[int] = mapped_column(
        ForeignKey(
            "monitors.id",
            ondelete="CASCADE",
        )
    )
    status: Mapped[str] = mapped_column()
    http_status_code: Mapped[int | None] = mapped_column()
    error_type: Mapped[str | None] = mapped_column()
    duration_ms: Mapped[int] = mapped_column()
    checked_at: Mapped[datetime] = mapped_column()
