from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from operations.database_migrations import create_tables
from router_library import book_router, user_router, reading_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Приложение запускается...")

    try:
        await create_tables()
        print("✅ Таблицы в БД готовы")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise

    yield

    print("🛑 Приложение останавливается...")


app = FastAPI(
    title="Personal Library API",
    description="API для ведения личной библиотеки и отслеживания прогресса чтения",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Personal Library API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "api": "running"
    }


app.include_router(book_router)
app.include_router(user_router)
app.include_router(reading_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )