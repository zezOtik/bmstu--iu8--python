from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, BIGINT
from datetime import datetime
from zoneinfo import ZoneInfo


def utc_now() -> datetime:
    return datetime.now(ZoneInfo("UTC"))


class TableModel(DeclarativeBase):
    pass


class OrderOrm(TableModel):
    __tablename__ = "order"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    customer_id: Mapped[int]
    desc: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now
    )
    status: Mapped[str] = mapped_column(
        default='new'
    )
