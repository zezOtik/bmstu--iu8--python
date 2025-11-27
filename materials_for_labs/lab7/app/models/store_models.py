from pydantic import BaseModel, AfterValidator, Field, ConfigDict, RootModel
from typing import Annotated, Literal, Optional, List
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
    customer_id: int
    desc: str | None = None
    created_at: Optional[AwareDatetime] = Field(default_factory=default_execution_time)
    status: Literal['new', 'delivery', 'finished']


class OrderAdd(OrderBase):
    pass


class OrderGet(OrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderListGet(RootModel[List[OrderGet]]):
    model_config = ConfigDict(from_attributes=True)