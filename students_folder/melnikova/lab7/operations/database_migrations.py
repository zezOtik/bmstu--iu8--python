from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from models.database_models import TableModel

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/meeting_rooms_db",
    echo=True
)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.create_all)

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.drop_all)