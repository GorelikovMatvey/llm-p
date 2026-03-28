"""Точка входа FastAPI-приложения.

Создаёт экземпляр приложения, подключает роутеры,
регистрирует событие startup для инициализации базы данных
и предоставляет технический эндпоинт /health.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управлять жизненным циклом приложения.

    При старте создаёт все таблицы базы данных, если они не существуют.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    """Собрать и вернуть экземпляр FastAPI-приложения.

    Подключает роутеры аутентификации и чата,
    регистрирует lifespan-обработчик и эндпоинт /health.

    Returns:
        Настроенный экземпляр FastAPI.
    """
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.include_router(auth_router)
    app.include_router(chat_router)

    @app.get("/health", tags=["health"], summary="Проверка состояния сервера")
    async def health() -> dict:
        """Вернуть статус сервера и текущее окружение.

        Returns:
            Словарь с полями status и env.
        """
        return {"status": "ok", "env": settings.env}

    return app


app = create_app()
