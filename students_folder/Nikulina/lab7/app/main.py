from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.operations.database_migrations import create_table, delete_table
from app.router_habits import router as habits_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    print("Таблицы созданы")
    yield
    await delete_table()
    print("Таблицы удалены")

app = FastAPI(lifespan=lifespan)
app.include_router(habits_router)
