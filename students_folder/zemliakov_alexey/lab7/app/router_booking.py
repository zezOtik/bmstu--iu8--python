from fastapi import APIRouter, Depends

from app.operations.database_operations import BookingWorkflow
from app.models.store_models import BookingReserve, DeleteBookingReserve, UserBookingGet, UserBookingGetRes, RoomFreeGet

from typing import List

router = APIRouter(
    prefix="/booking",
    tags=["бронирования"],
)


@router.post(
    "/add_booking",
    summary="Добавление бронирования")
async def add_booking(booking: BookingReserve = Depends()) -> dict:
    try:
        id = await BookingWorkflow.reserve_room(booking)
    except ValueError:
        return {"error": "unprocessable entity"}
    except KeyError:
        return {"error": "this room reserved for this time"}
    return {"id": id}


@router.get("/get_users_booking",
            summary="Получение бронирований пользователя")
async def get_rooms(user: UserBookingGet = Depends()) -> List[UserBookingGetRes]:
    rooms = await BookingWorkflow.get_users_booking(user)
    return rooms


@router.delete("/delete_booking",
               summary="Удаление бронирования пользователя")
async def get_rooms(user: DeleteBookingReserve = Depends()) -> str:
    res = await BookingWorkflow.delete_reserve_room(user)
    return res


@router.get("/check_room",
            summary="Проверка доступности бронирования комнаты на время")
async def get_rooms(room: RoomFreeGet = Depends()) -> bool:
    res = await BookingWorkflow.check_available(room)
    return res
