from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from operations.database_operations import RoomWorkflow, BookingWorkflow
from models.store_models import (
    RoomAdd, RoomGet,
    BookingAdd, BookingGet,
    RoomAvailability, UserBookings
)

router = APIRouter(
    prefix="/api",
    tags=["Бронирование переговорок"]
)


# Room endpoints
@router.post("/rooms", response_model=dict, summary="Создание новой переговорки")
async def create_room(room: RoomAdd = Depends()) -> dict:
    try:
        room_id = await RoomWorkflow.add_room(room)
        return {"id": room_id, "message": "Room created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms", response_model=List[RoomGet], summary="Получение списка всех переговорок")
async def get_all_rooms() -> List[RoomGet]:
    try:
        return await RoomWorkflow.get_all_rooms()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}", response_model=RoomGet, summary="Получение информации о переговорке")
async def get_room(room_id: int) -> RoomGet:
    try:
        room = await RoomWorkflow.get_room_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Booking endpoints
@router.post("/bookings", response_model=dict, summary="Создание бронирования")
async def create_booking(booking: BookingAdd = Depends()) -> dict:
    try:
        booking_id = await BookingWorkflow.create_booking(booking)
        return {"id": booking_id, "message": "Booking created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bookings/{booking_id}", response_model=dict, summary="Удаление бронирования")
async def delete_booking(booking_id: int) -> dict:
    try:
        success = await BookingWorkflow.delete_booking(booking_id)
        if not success:
            raise HTTPException(status_code=404, detail="Booking not found")
        return {"message": "Booking deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/availability", response_model=RoomAvailability, summary="Проверка доступности комнаты")
async def check_availability(
    room_id: int = Query(..., description="ID комнаты"),
    start_time: datetime = Query(..., description="Время начала (с часовым поясом)"),
    end_time: datetime = Query(..., description="Время окончания (с часовым поясом)")
) -> RoomAvailability:
    try:
        return await BookingWorkflow.check_room_availability(room_id, start_time, end_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings/user/{user_name}", response_model=UserBookings, summary="Получение бронирований пользователя")
async def get_user_bookings(user_name: str) -> UserBookings:
    try:
        bookings = await BookingWorkflow.get_user_bookings(user_name)
        return UserBookings(user_name=user_name, bookings=bookings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings", response_model=List[BookingGet], summary="Получение всех бронирований")
async def get_all_bookings() -> List[BookingGet]:
    try:
        return await BookingWorkflow.get_all_bookings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))