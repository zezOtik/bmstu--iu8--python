from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, BIGINT, ForeignKey
from datetime import datetime
from zoneinfo import ZoneInfo


def utc_now() -> datetime:
    return datetime.now(ZoneInfo("UTC"))


class TableModel(DeclarativeBase):
    pass


class RoomORM(TableModel):
    __tablename__ = "room"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    name: Mapped[str]
    capacity: Mapped[int]
    location: Mapped[str]


class BookingORM(TableModel):
    __tablename__ = "booking"
    __table_args__ = {"schema": "public"}
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("public.room.id"))
    user_name: Mapped[str]
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
