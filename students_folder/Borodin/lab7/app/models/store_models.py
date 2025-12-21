from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo
from enum import Enum


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt


class StatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserGet(UserBase):
    id: int

    model_config = {"from_attributes": True}


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: StatusEnum = StatusEnum.pending
    due_date: datetime
    assignee_id: int

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v):
        if isinstance(v, str):
            v = datetime.fromisoformat(v)
        return ensure_utc(v)

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, v):
        now = datetime.now(ZoneInfo("UTC"))
        if v < now:
            raise ValueError("due_date must be in the future")
        return v


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v)
        return ensure_utc(v)


class TaskGet(TaskBase):
    id: int

    model_config = {"from_attributes": True}


class TaskListGet(BaseModel):
    tasks: List[TaskGet]


class TasksByUser(BaseModel):
    user_id: int