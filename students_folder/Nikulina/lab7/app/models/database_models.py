from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, BIGINT, Integer, Text
from datetime import datetime
from zoneinfo import ZoneInfo

def utc_now():
    return datetime.now(ZoneInfo("UTC"))

class TableModel(DeclarativeBase):
    pass

class HabitOrm(TableModel):
    __tablename__ = "habit"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str | None]

class CompletionOrm(TableModel):
    __tablename__ = "completion"
    __table_args__ = {"schema": "public"}

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    habit_id: Mapped[int]
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
