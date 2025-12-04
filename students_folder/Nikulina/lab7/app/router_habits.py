from fastapi import APIRouter, Depends
from typing import List

from app.operations.database_operations import HabitWorkflow, CompletionWorkflow
from app.models.store_models import (
    HabitAdd, HabitGet, CompletionAdd, CompletionGet
)

router = APIRouter(
    prefix="/habits",
    tags=["Habits"],
)

@router.post("/add", summary="Создание привычки")
async def add_habit(habit: HabitAdd = Depends(HabitAdd)) -> dict:
    new_id = await HabitWorkflow.add_habit(habit)
    return {"id": new_id}

@router.get("/all", summary="Список привычек")
async def get_habits() -> List[HabitGet]:
    return await HabitWorkflow.get_habits()

@router.post("/complete", summary="Отметка выполнения привычки")
async def add_completion(c: CompletionAdd = Depends(CompletionAdd)) -> dict:
    new_id = await CompletionWorkflow.add_completion(c)
    return {"id": new_id}

@router.get("/{habit_id}/completions", summary="Получение всех выполнений привычки")
async def get_completions(habit_id: int) -> List[CompletionGet]:
    return await CompletionWorkflow.get_completions(habit_id)

@router.get("/{habit_id}/streak", summary="Серия подряд выполненных дней")
async def get_streak(habit_id: int) -> dict:
    streak = await CompletionWorkflow.get_streak(habit_id)
    return {"streak": streak}
