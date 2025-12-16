from app.models.database_models import RoomORM, BookingORM
from app.models.store_models import RoomAdd,RoomFreeGet, RoomListGet, BookingReserve, DeleteBookingReserve, UserBookingGet, UserBookingGetRes,  BookingListGet
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import select, delete
from typing import List

engine = create_async_engine("postgresql+asyncpg://postgres:postgres@postgres_container:5432/postgres")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class RoomWorkflow:
    @classmethod
    async def add_room(cls, room: RoomAdd) -> int:
        async with new_session() as session:
            data = room.model_dump()
            new_room = RoomORM(**data)
            session.add(new_room)
            await session.flush()
            await session.commit()
            return new_room.id

    @classmethod
    async def get_rooms(cls) -> RoomListGet:
        async with new_session() as session:
            query = select(RoomORM)
            result = await session.execute(query)
            room_models = result.scalars().all()

            rooms = RoomListGet.model_validate(room_models)
            return rooms.root


class BookingWorkflow:
    @classmethod
    async def reserve_room(cls, booking: BookingReserve) -> int:
        async with new_session() as session:
            data = booking.model_dump()
            # проверка на доступность
            new_booking = BookingORM(**data)
            session.add(new_booking)
            await session.flush()
            await session.commit()
            return new_booking.id

    @classmethod
    async def delete_reserve_room(cls, booking: DeleteBookingReserve) -> str:
        async with new_session() as session:
            data = booking.model_dump()
            query = delete(BookingORM).where(BookingORM.id == data["booking_id"] and BookingORM.user_name == data["user_name"])
            results = await session.execute(query)
            await session.commit()
            if results.rowcount() > 0:
                return f"success deleted {results.rowcount()} rows"

            return "nothing for delete"

    @classmethod
    async def get_users_booking(cls, user: UserBookingGet) -> List[UserBookingGetRes]:
        async with new_session() as session:
            data = user.model_dump()
            query = select(BookingORM).where(BookingORM.user_name == data["user_name"])
            result = await session.execute(query)
            await session.commit()
            res = []
            for row in result:
                print(row)

            return res

    @classmethod
    async def check_available(cls, free_room: RoomFreeGet) -> bool:
        async with new_session() as session:
            data = free_room.model_dump()
            query = select(BookingORM).where(BookingORM.room_id == data["id"])
            result = await session.execute(query)
            room_models = result.scalars().all()
            return True
