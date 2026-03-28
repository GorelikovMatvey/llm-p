"""Pydantic-схемы для работы с чатом.

Используются в эндпоинтах отправки запроса к LLM
и получения истории диалога.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Параметры запроса к языковой модели.

    Attributes:
        prompt: Основной текст запроса пользователя.
        system: Необязательная системная инструкция для модели.
        max_history: Количество сообщений из истории,
            включаемых в контекст запроса.
        temperature: Параметр случайности ответа модели.
            0.0 — детерминированный, 2.0 — максимально случайный.
    """

    prompt: str
    system: str | None = None
    max_history: int = Field(default=10, ge=0)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    """Ответ языковой модели.

    Attributes:
        answer: Текст ответа, сгенерированный моделью.
    """

    answer: str


class ChatMessagePublic(BaseModel):
    """Публичное представление сообщения из истории диалога.

    Attributes:
        id: Уникальный идентификатор сообщения.
        role: Роль отправителя — "user" или "assistant".
        content: Текст сообщения.
        created_at: Дата и время создания сообщения в UTC.
    """

    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
