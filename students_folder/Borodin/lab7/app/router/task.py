from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.store_models import TaskCreate, TaskUpdate, TaskGet, TasksByUser
from app.operations.task_ops import (
    create_task,
    update_task,
    get_tasks_by_status,
    get_tasks_by_user,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskGet)
async def create_new_task(task: TaskCreate):
    return await create_task(task)

@router.put("/{task_id}", response_model=TaskGet)
async def update_existing_task(task_id: int, task: TaskUpdate):
    return await update_task(task_id, task)

@router.get("/by-status", response_model=List[TaskGet])
async def read_tasks_by_status(status: str = Query(...)):
    return await get_tasks_by_status(status)

@router.get("/user/{user_id}", response_model=List[TaskGet])
async def read_tasks_for_user(user_id: int):
    return await get_tasks_by_user(user_id)