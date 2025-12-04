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
            result = await session.execute(
                select(CompletionOrm.date).where(
                    CompletionOrm.habit_id == habit_id
                ).order_by(CompletionOrm.date.desc())
            )
            dates = [row for row, in result.all()]

            if not dates:
                return 0

            streak = 0
            today = datetime.now(timezone.utc).date()

            for i, day in enumerate(dates):
                if day.date() == today - timedelta(days=streak):
                    streak += 1
                else:
                    break

            return streak
