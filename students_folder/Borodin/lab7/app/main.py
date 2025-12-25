from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.operations.base import engine
from app.models.database_models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

from app.router.user import router as user_router
from app.router.task import router as task_router

app.include_router(user_router)
app.include_router(task_router)