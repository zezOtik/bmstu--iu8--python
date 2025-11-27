from app.operations.database_migrations import create_table, delete_table

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.router_order import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    print("Таблица готова")
    yield
    await delete_table()
    print("Таблица очищена")


app = FastAPI(lifespan=lifespan)

app.include_router(orders_router)