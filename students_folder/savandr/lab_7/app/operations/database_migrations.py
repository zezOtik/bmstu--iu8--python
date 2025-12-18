from sqlalchemy.ext.asyncio import create_async_engine
from ..models.database_models import TableModel


engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.create_all)
    print("✅ Таблицы успешно созданы в БД")


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.drop_all)
    print("🗑️  Таблицы успешно удалены из БД")