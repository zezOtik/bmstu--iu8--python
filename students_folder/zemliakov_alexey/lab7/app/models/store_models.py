from pydantic import BaseModel, AfterValidator, Field, ConfigDict, RootModel, model_validator
from typing_extensions import Self
from typing import Annotated, Literal, List
from datetime import datetime
from zoneinfo import ZoneInfo


# 2025-04-05T12:00:00Z
def validate_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return dt


AwareDatetime = Annotated[datetime, AfterValidator(validate_aware)]


def default_execution_time():
    return datetime.now(ZoneInfo("UTC"))


class Room(BaseModel):
    name: str
    capacity: int
    location: str


class RoomAdd(Room):
    pass


class RoomGet(Room):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomListGet(RootModel[List[RoomGet]]):
    model_config = ConfigDict(from_attributes=True)


class RoomFreeGet(BaseModel):
    id: int
    start_time: AwareDatetime = Field(default_factory=default_execution_time)
    end_time: AwareDatetime = Field(default_factory=default_execution_time)

    model_config = ConfigDict(from_attributes=True)


class Booking(BaseModel):
    room_id: int
    user_name: str
    start_time: AwareDatetime = Field(default_factory=default_execution_time)
    end_time: AwareDatetime = Field(default_factory=default_execution_time)

    @model_validator(mode="after")
    def check_date(self) -> Self:
        if self.start_time >= self.end_time:
            raise ValueError("start date must be before end")
        return self


class BookingReserve(Booking):
    pass


class DeleteBookingReserve(BaseModel):
    booking_id: int
    user_name: str

    model_config = ConfigDict(from_attributes=True)


class UserBookingGet(BaseModel):
    user_name: str

    model_config = ConfigDict(from_attributes=True)


class UserBookingGetRes(Booking):
    id: int

    model_config = ConfigDict(from_attributes=True)
