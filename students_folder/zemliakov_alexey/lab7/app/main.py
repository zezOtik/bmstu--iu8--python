from fastapi import FastAPI

from app.router_room import router as room_router

from app.router_booking import router as booking_router

from app.operations.database_migrations import create_table, delete_table

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    print("Таблица готова")
    yield
    await delete_table()
    print("Таблица очищена")


app = FastAPI(lifespan=lifespan)

app.include_router(room_router)
app.include_router(booking_router)
