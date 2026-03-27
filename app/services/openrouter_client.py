"""Клиент для взаимодействия с OpenRouter API.

Отвечает только за HTTP-коммуникацию с внешним сервисом.
Не работает с базой данных и не знает о пользователях.
"""

import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    """HTTP-клиент для отправки запросов к OpenRouter.

    Формирует заголовки и тело запроса согласно спецификации
    OpenRouter API и обрабатывает ошибки внешнего сервиса.
    """

    async def complete(self, messages: list[dict],
                       temperature: float = 0.7) -> str:
        """Отправить запрос к языковой модели и получить ответ.

        Выполняет POST-запрос к эндпоинту /chat/completions OpenRouter
        с переданным списком сообщений и параметрами модели.

        Args:
            messages: Список сообщений в формате OpenAI —
                каждое сообщение содержит поля "role" и "content".
            temperature: Параметр случайности генерации ответа.
                0.0 — детерминированный, 2.0 — максимально случайный.

        Returns:
            Текст ответа языковой модели.

        Raises:
            ExternalServiceError: Если OpenRouter вернул код ошибки.
        """
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )

        if response.status_code != 200:
            raise ExternalServiceError(
                f"OpenRouter вернул ошибку:"
                f" {response.status_code} — {response.text}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]
