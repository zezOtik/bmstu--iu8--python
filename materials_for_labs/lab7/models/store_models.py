from pydantic import BaseModel, AfterValidator, Field
from typing import Annotated, Literal
from datetime import datetime
from zoneinfo import ZoneInfo


def validate_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return dt


AwareDatetime = Annotated[datetime, AfterValidator(validate_aware)]

def default_execution_time():
    return datetime.now(ZoneInfo("UTC"))


class OrderBase(BaseModel):
    id: int
    customer_id: int
    desc: str | None = None
    created_at: AwareDatetime = Field(default_factory=default_execution_time)
    status: Literal['new', 'delivery', 'finished']


class OrderAdd(OrderBase):
    pass
