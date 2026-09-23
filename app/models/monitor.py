from datetime import datetime

from sqlalchemy import DateTime, true
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MonitorModel(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True,))
    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default=true(),
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
