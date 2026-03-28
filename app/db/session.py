"""Настройка подключения к базе данных.

Создаёт асинхронный engine SQLAlchemy и фабрику сессий.
Файл содержит только инфраструктуру подключения —
никаких запросов к таблицам здесь нет.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

DATABASE_URL = f"sqlite+aiosqlite:///{settings.sqlite_path}"
"""Строка подключения к SQLite в асинхронном режиме."""

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
"""Асинхронный engine SQLAlchemy.

check_same_thread=False необходим для SQLite при работе
в асинхронном окружении с несколькими корутинами.
"""

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
"""Фабрика асинхронных сессий.

expire_on_commit=False предотвращает сброс атрибутов ORM-объектов
после завершения транзакции, что позволяет использовать их
за пределами сессии.
"""
