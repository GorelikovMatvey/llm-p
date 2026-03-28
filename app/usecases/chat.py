"""Бизнес-логика взаимодействия с языковой моделью.

Формирует контекст запроса, управляет историей диалога
и координирует работу между репозиторием и клиентом OpenRouter.
Не создаёт сессии базы данных напрямую.
"""

from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    """Usecase для отправки запросов к LLM и управления историей диалога.

    Attributes:
        _chat_repo: Репозиторий сообщений чата.
        _openrouter: Клиент OpenRouter.
    """

    def __init__(
            self,
            chat_repo: ChatMessageRepository,
            openrouter_client: OpenRouterClient,
    ) -> None:
        """Инициализировать usecase с репозиторием и клиентом OpenRouter.

        Args:
            chat_repo: Репозиторий для работы с таблицей chat_messages.
            openrouter_client: HTTP-клиент для запросов к OpenRouter.
        """
        self._chat_repo = chat_repo
        self._openrouter = openrouter_client

    async def ask(
            self,
            user_id: int,
            prompt: str,
            system: str | None = None,
            max_history: int = 10,
            temperature: float = 0.7,
    ) -> str:
        """Отправить запрос к языковой модели и сохранить диалог.

        Порядок действий:
            1. Формирует список messages: system → история → prompt.
            2. Сохраняет prompt в базе как сообщение роли "user".
            3. Отправляет запрос в OpenRouter.
            4. Сохраняет ответ в базе как сообщение роли "assistant".

        Args:
            user_id: Идентификатор текущего пользователя.
            prompt: Текст запроса пользователя.
            system: Необязательная системная инструкция для модели.
            max_history: Количество предыдущих сообщений для контекста.
            temperature: Параметр случайности генерации ответа.

        Returns:
            Текст ответа языковой модели.

        Raises:
            ExternalServiceError: Если OpenRouter вернул ошибку.
        """
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        history = await self._chat_repo.get_last_n(user_id=user_id,
                                                   n=max_history)
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": prompt})

        await self._chat_repo.add(user_id=user_id, role="user", content=prompt)

        answer = await self._openrouter.complete(messages,
                                                 temperature=temperature)

        await self._chat_repo.add(user_id=user_id, role="assistant",
                                  content=answer)

        return answer

    async def get_history(
            self, user_id: int, n: int = 50
    ) -> list[ChatMessage]:
        """Получить историю диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.
            n: Максимальное количество возвращаемых сообщений.

        Returns:
            Список сообщений в хронологическом порядке.
        """
        return await self._chat_repo.get_last_n(user_id=user_id, n=n)

    async def clear_history(self, user_id: int) -> None:
        """Удалить всю историю диалога пользователя.

        Args:
            user_id: Идентификатор пользователя.
        """
        await self._chat_repo.delete_all(user_id=user_id)
