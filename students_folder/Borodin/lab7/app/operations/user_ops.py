from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.operations.base import AsyncSessionLocal
from app.models.database_models import UserORM
from app.models.store_models import UserCreate


async def create_user(user_in: UserCreate):
    async with AsyncSessionLocal() as session:
        user = UserORM(**user_in.model_dump())
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            await session.rollback()
            raise ValueError("User with this email already exists")
        return user


async def update_user(user_id: int, user_in: UserCreate):
    async with AsyncSessionLocal() as session:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(**user_in.model_dump())
            .returning(UserORM)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.scalar_one()


async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one()