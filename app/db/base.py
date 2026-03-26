"""Базовый класс для ORM-моделей SQLAlchemy.

Все модели приложения наследуются от Base, что позволяет SQLAlchemy
отслеживать их метаданные и управлять схемой базы данных.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый декларативный класс для всех ORM-моделей приложения."""