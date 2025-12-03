from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.models.database_models import TableModel

# тут мы создаем бд по модели

# движок
engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        connect_args={"ssl": False}
        )
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def create_table():
   async with engine.begin() as conn:
       await conn.run_sync(TableModel.metadata.create_all) # асинхронное подключение к БД
       #metadata.create_all() — синхронный метод в либе, но через run_sync запускаем его асинхронно
       # а вообще он генерит все sql запросы по списочку созданному
       print("Таблицы созданы успешно!")

async def delete_table():
   async with engine.begin() as conn:
       await conn.run_sync(TableModel.metadata.drop_all)
       print("Таблицы удалены")