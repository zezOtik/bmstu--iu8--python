from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from operations.database_migrations import create_tables, delete_tables
from routers.booking_router import router as booking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при запуске
    print("Creating tables...")
    await create_tables()
    print("Tables created successfully")

    yield

    # Очищаем таблицы при остановке (опционально)
    # print("Deleting tables...")
    # await delete_tables()
    # print("Tables deleted successfully")


app = FastAPI(
    title="Meeting Room Booking API",
    description="API для резервирования переговорок в офисе",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер
app.include_router(booking_router)


@app.get("/", summary="Главная страница")
async def root():
    return {
        "message": "Meeting Room Booking API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", summary="Проверка здоровья приложения")
async def health_check():
    return {"status": "healthy"}