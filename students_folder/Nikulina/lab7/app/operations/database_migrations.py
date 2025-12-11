from sqlalchemy.ext.asyncio import create_async_engine
from app.models.database_models import TableModel

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"
)

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.create_all)

async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.drop_all)
