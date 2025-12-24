from pydantic import BaseModel, AfterValidator, Field, ConfigDict, RootModel, field_validator
from typing import Annotated, Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo


def validate_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("datetime must include timezone information")
    return dt


AwareDatetime = Annotated[datetime, AfterValidator(validate_aware)]


def default_time_now():
    return datetime.now(ZoneInfo("UTC"))


# Room models
class RoomBase(BaseModel):
    name: str
    capacity: int
    location: str


class RoomAdd(RoomBase):
    pass


class RoomGet(RoomBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomListGet(RootModel[List[RoomGet]]):
    model_config = ConfigDict(from_attributes=True)


# Booking models
class BookingBase(BaseModel):
    room_id: int
    user_name: str
    start_time: AwareDatetime
    end_time: AwareDatetime

    @field_validator('end_time')
    def validate_time_range(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class BookingAdd(BookingBase):
    pass


class BookingGet(BookingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BookingListGet(RootModel[List[BookingGet]]):
    model_config = ConfigDict(from_attributes=True)


# Response models
class RoomAvailability(BaseModel):
    is_available: bool
    conflicting_bookings: Optional[List[BookingGet]] = None


class UserBookings(BaseModel):
    user_name: str
    bookings: List[BookingGet]