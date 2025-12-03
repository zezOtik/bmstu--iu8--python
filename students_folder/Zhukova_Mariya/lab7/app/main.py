from app.operations.database_migrations import create_table,delete_table
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.router_blog import router as blog_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    print("Таблицы созданы")
    yield
    # await delete_table()
    # print("Таблицы очищены")


app = FastAPI(lifespan=lifespan)
app.include_router(blog_router)


# uvicorn app.main:app --reload - запуск, с reload будет автоматически выводить все изменения на локалхост, даже в тестовом файле