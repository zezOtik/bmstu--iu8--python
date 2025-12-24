from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, BIGINT, String, Integer, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from zoneinfo import ZoneInfo


def utc_now() -> datetime:
    return datetime.now(ZoneInfo("UTC"))


class TableModel(DeclarativeBase):
    pass


class RoomOrm(TableModel):
    __tablename__ = "room"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)


class BookingOrm(TableModel):
    __tablename__ = "booking"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("public.room.id"), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )