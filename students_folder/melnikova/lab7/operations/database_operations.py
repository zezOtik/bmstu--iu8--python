from models.database_models import RoomOrm, BookingOrm
from models.store_models import RoomAdd, RoomGet, RoomListGet, BookingAdd, BookingGet, BookingListGet, \
    RoomAvailability
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime

# Настройки подключения к БД
engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/meeting_rooms_db",
    echo=True
)
new_session = async_sessionmaker(engine, expire_on_commit=False)


class RoomWorkflow:
    @classmethod
    async def add_room(cls, room: RoomAdd) -> int:
        async with new_session() as session:
            data = room.model_dump()
            new_room = RoomOrm(**data)
            session.add(new_room)
            await session.flush()
            await session.commit()
            return new_room.id

    @classmethod
    async def get_all_rooms(cls) -> List[RoomGet]:
        async with new_session() as session:
            query = select(RoomOrm)
            result = await session.execute(query)
            room_models = result.scalars().all()

            rooms = RoomListGet.model_validate(room_models)
            return rooms.root

    @classmethod
    async def get_room_by_id(cls, room_id: int) -> Optional[RoomGet]:
        async with new_session() as session:
            query = select(RoomOrm).where(RoomOrm.id == room_id)
            result = await session.execute(query)
            room = result.scalar_one_or_none()

            if room:
                return RoomGet.model_validate(room)
            return None


class BookingWorkflow:
    @classmethod
    async def create_booking(cls, booking: BookingAdd) -> int:
        async with new_session() as session:
            # Проверка доступности комнаты
            is_available = await cls.check_room_availability(
                booking.room_id,
                booking.start_time,
                booking.end_time
            )

            if not is_available:
                raise ValueError("Room is not available for the selected time period")

            data = booking.model_dump()
            new_booking = BookingOrm(**data)
            session.add(new_booking)
            await session.flush()
            await session.commit()
            return new_booking.id

    @classmethod
    async def delete_booking(cls, booking_id: int) -> bool:
        async with new_session() as session:
            query = select(BookingOrm).where(BookingOrm.id == booking_id)
            result = await session.execute(query)
            booking = result.scalar_one_or_none()

            if booking:
                await session.delete(booking)
                await session.commit()
                return True
            return False

    @classmethod
    async def check_room_availability(cls, room_id: int, start_time: datetime, end_time: datetime) -> RoomAvailability:
        async with new_session() as session:
            # Ищем пересекающиеся бронирования
            query = select(BookingOrm).where(
                and_(
                    BookingOrm.room_id == room_id,
                    or_(
                        and_(
                            BookingOrm.start_time < end_time,
                            BookingOrm.end_time > start_time
                        ),
                        BookingOrm.start_time == start_time,
                        BookingOrm.end_time == end_time
                    )
                )
            )
            result = await session.execute(query)
            conflicting_bookings = result.scalars().all()

            is_available = len(conflicting_bookings) == 0

            conflicting_list = None
            if not is_available:
                conflicting_list = BookingListGet.model_validate(conflicting_bookings).root

            return RoomAvailability(
                is_available=is_available,
                conflicting_bookings=conflicting_list
            )

    @classmethod
    async def get_user_bookings(cls, user_name: str) -> List[BookingGet]:
        async with new_session() as session:
            query = select(BookingOrm).where(BookingOrm.user_name == user_name)
            result = await session.execute(query)
            booking_models = result.scalars().all()

            bookings = BookingListGet.model_validate(booking_models)
            return bookings.root

    @classmethod
    async def get_all_bookings(cls) -> List[BookingGet]:
        async with new_session() as session:
            query = select(BookingOrm)
            result = await session.execute(query)
            booking_models = result.scalars().all()

            bookings = BookingListGet.model_validate(booking_models)
            return bookings.root

    @classmethod
    async def get_booking_by_id(cls, booking_id: int) -> Optional[BookingGet]:
        async with new_session() as session:
            query = select(BookingOrm).where(BookingOrm.id == booking_id)
            result = await session.execute(query)
            booking = result.scalar_one_or_none()

            if booking:
                return BookingGet.model_validate(booking)
            return None