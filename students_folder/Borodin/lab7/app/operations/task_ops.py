from sqlalchemy import select, update
from app.operations.base import AsyncSessionLocal
from app.models.database_models import TaskORM, StatusEnum
from app.models.store_models import TaskCreate, TaskUpdate


async def create_task(task_in: TaskCreate):
    async with AsyncSessionLocal() as session:
        task = TaskORM(**task_in.model_dump())
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


async def update_task(task_id: int, task_in: TaskUpdate):
    async with AsyncSessionLocal() as session:
        values = {k: v for k, v in task_in.model_dump().items() if v is not None}
        stmt = (
            update(TaskORM)
            .where(TaskORM.id == task_id)
            .values(**values)
            .returning(TaskORM)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one()


async def get_tasks_by_status(status: str):
    async with AsyncSessionLocal() as session:
        stmt = select(TaskORM).where(TaskORM.status == StatusEnum(status))
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_tasks_by_user(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(TaskORM).where(TaskORM.assignee_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()