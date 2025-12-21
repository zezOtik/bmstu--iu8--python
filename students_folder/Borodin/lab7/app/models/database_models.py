from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from enum import Enum as PyEnum
from zoneinfo import ZoneInfo


def utc_now():
    return datetime.now(ZoneInfo("UTC"))


class StatusEnum(PyEnum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)


class TaskORM(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum), default=StatusEnum.pending)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    assignee_id: Mapped[int] = mapped_column(ForeignKey("user.id"))