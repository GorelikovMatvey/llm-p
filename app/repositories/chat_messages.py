"""Репозиторий сообщений чата.

Содержит только операции доступа к данным таблицы chat_messages.
Не обращается к OpenRouter и не формирует логику
отбора сообщений для контекста модели.
"""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


class ChatMessageRepository:
    """Репозиторий для работы с таблицей chat_messages.

    Выполняет операции добавления, чтения и удаления
    сообщений диалога пользователя.

    Attributes:
        _session: Асинхронная сессия базы данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализировать репозиторий с сессией базы данных.

        Args:
            session: Асинхронная сессия SQLAlchemy.
        """
        self._session = session

    async def add(self, user_id: int, role: str, content: str) -> ChatMessage:
        """Добавить новое сообщение в историю диалога.

        Args:
            user_id: Идентификатор пользователя-владельца сообщения.
            role: Роль отправителя — "user" или "assistant".
            content: Текст сообщения.

        Returns:
            Созданный ORM-объект сообщения с заполненным id.
        """
        message = ChatMessage(user_id=user_id, role=role, content=content)
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message

    async def get_last_n(self, user_id: int, n: int) -> list[ChatMessage]:
        """Получить последние сообщения пользователя в хронологическом порядке.

        Выбирает N последних сообщений по убыванию даты,
        затем разворачивает список для хронологического порядка.

        Args:
            user_id: Идентификатор пользователя.
            n: Максимальное количество сообщений.

        Returns:
            Список сообщений от старых к новым.
        """
        result = await self._session.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(n)
        )
        messages = result.scalars().all()
        return list(reversed(messages))

    async def delete_all(self, user_id: int) -> None:
        """Удалить всю историю диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.
        """
        await self._session.execute(
            delete(ChatMessage).where(ChatMessage.user_id == user_id)
        )
        await self._session.commit()
