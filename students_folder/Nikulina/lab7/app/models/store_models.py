from pydantic import BaseModel, AfterValidator, Field, ConfigDict, RootModel
from typing import Annotated, List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

def validate_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return dt

AwareDatetime = Annotated[datetime, AfterValidator(validate_aware)]

def utc_now():
    return datetime.now(ZoneInfo("UTC"))

class HabitBase(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None

class HabitAdd(HabitBase):
    pass

class HabitGet(HabitBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class HabitListGet(RootModel[List[HabitGet]]):
    model_config = ConfigDict(from_attributes=True)

class CompletionBase(BaseModel):
    habit_id: int
    date: AwareDatetime = Field(default_factory=utc_now)

class CompletionAdd(CompletionBase):
    pass

class CompletionGet(CompletionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CompletionListGet(RootModel[List[CompletionGet]]):
    model_config = ConfigDict(from_attributes=True)
