from fastapi import APIRouter, Depends

from app.operations.database_operations import RoomWorkflow
from app.models.store_models import RoomAdd, RoomGet

from typing import List


router = APIRouter(
    prefix="/rooms",
    tags=["комнаты"],
)

@router.post(
    "/add_room",
    summary="Добавление новой комнаты")
async def add_room(room: RoomAdd = Depends()) -> dict:
    id = await RoomWorkflow.add_room(room)
    return {"id": id}

@router.get("/get_rooms",
            summary="Получение комнат")
async def get_rooms() -> List[RoomGet]:
    rooms = await RoomWorkflow.get_rooms()
    return rooms