from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.models.database_models import TableModel
import os

# Получаем URL из переменных окружения, с fallback на localhost для разработки
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
)

# Создаем движок
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": False}
)
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.create_all)
        print("Таблицы созданы успешно!")

async def delete_table():
    async with engine.begin() as conn:
        await conn.run_sync(TableModel.metadata.drop_all)
        print("Таблицы удалены")