from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import select, func
from typing import List
from datetime import timedelta, datetime, timezone

from app.models.database_models import HabitOrm, CompletionOrm
from app.models.store_models import (
    HabitAdd, HabitListGet, HabitGet,
    CompletionAdd, CompletionListGet, CompletionGet
)

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"
)
new_session = async_sessionmaker(engine, expire_on_commit=False)

class HabitWorkflow:

    @classmethod
    async def add_habit(cls, habit: HabitAdd) -> int:
        async with new_session() as session:
            data = habit.model_dump()
            model = HabitOrm(**data)
            session.add(model)
            await session.flush()
            await session.commit()
            return model.id

    @classmethod
    async def get_habits(cls) -> HabitListGet:
        async with new_session() as session:
            result = await session.execute(select(HabitOrm))
            models = result.scalars().all()
            return HabitListGet.model_validate(models).root

class CompletionWorkflow:

    @classmethod
    async def add_completion(cls, comp: CompletionAdd) -> int:
        async with new_session() as session:
            data = comp.model_dump()
            model = CompletionOrm(**data)
            session.add(model)
            await session.flush()
            await session.commit()
            return model.id

    @classmethod
    async def get_completions(cls, habit_id: int) -> CompletionListGet:
        async with new_session() as session:
            result = await session.execute(
                select(CompletionOrm).where(CompletionOrm.habit_id == habit_id)
            )
            models = result.scalars().all()
            return CompletionListGet.model_validate(models).root

    @classmethod
    async def get_streak(cls, habit_id: int) -> int:
        async with new_session() as session:
            query = select(CompletionOrm).where(CompletionOrm.habit_id == habit_id).order_by(CompletionOrm.date.desc())
            result = await session.execute(query)
            completions = result.scalars().all()

            if not completions:
                return 0

            current_date = completions[0].date.date()
            streak = 1

            for comp in completions[1:]:
                comp_date = comp.date.date()
                if current_date - comp_date == timedelta(days=1):
                    streak += 1
                    current_date = comp_date
                else:
                    break

            return streak

