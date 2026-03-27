"""Репозиторий пользователей.

Содержит только операции доступа к данным таблицы users.
Не выполняет хеширование паролей и не создаёт JWT-токены.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:
    """Репозиторий для работы с таблицей users.

    Принимает асинхронную сессию SQLAlchemy и выполняет
    операции чтения и записи пользователей.

    Attributes:
        _session: Асинхронная сессия базы данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализировать репозиторий с сессией базы данных.

        Args:
            session: Асинхронная сессия SQLAlchemy.
        """
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email.

        Args:
            email: Email пользователя.

        Returns:
            ORM-объект пользователя или None если не найден.
        """
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Найти пользователя по ID.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            ORM-объект пользователя или None если не найден.
        """
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str,
                     role: str = "user") -> User:
        """Создать нового пользователя и сохранить в базе данных.

        Args:
            email: Email нового пользователя.
            password_hash: Хеш пароля, вычисленный заранее.
            role: Роль пользователя (по умолчанию "user").

        Returns:
            Созданный ORM-объект пользователя с заполненным id.
        """
        user = User(email=email, password_hash=password_hash, role=role)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
