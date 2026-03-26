"""Эндпоинты для работы с чатом и историей диалога.

Маршруты:
    POST   /chat         — отправить запрос к LLM и получить ответ.
    GET    /chat/history — получить историю диалога текущего пользователя.
    DELETE /chat/history — очистить историю диалога текущего пользователя.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_chat_usecase, get_current_user_id
from app.core.errors import ExternalServiceError
from app.schemas.chat import ChatMessagePublic, ChatRequest, ChatResponse
from app.usecases.chat import ChatUseCase

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Отправить запрос к LLM",
)
async def chat(
        body: ChatRequest,
        user_id: int = Depends(get_current_user_id),
        usecase: ChatUseCase = Depends(get_chat_usecase),
) -> ChatResponse:
    """Отправить prompt языковой модели и получить ответ.

    Запрос и ответ сохраняются в истории диалога пользователя.

    Args:
        body: Параметры запроса: prompt, system, max_history, temperature.
        user_id: ID текущего пользователя из JWT.
        usecase: Usecase чата.

    Returns:
        Ответ языковой модели.

    Raises:
        HTTPException: 502 если OpenRouter вернул ошибку.
    """
    try:
        answer = await usecase.ask(
            user_id=user_id,
            prompt=body.prompt,
            system=body.system,
            max_history=body.max_history,
            temperature=body.temperature,
        )
        return ChatResponse(answer=answer)
    except ExternalServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=str(e))


@router.get(
    "/history",
    response_model=list[ChatMessagePublic],
    summary="История диалога",
)
async def get_history(
        user_id: int = Depends(get_current_user_id),
        usecase: ChatUseCase = Depends(get_chat_usecase),
) -> list[ChatMessagePublic]:
    """Вернуть историю диалога текущего пользователя.

    Args:
        user_id: ID текущего пользователя из JWT.
        usecase: Usecase чата.

    Returns:
        Список сообщений в хронологическом порядке.
    """
    return await usecase.get_history(user_id=user_id)


@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Очистить историю диалога",
)
async def delete_history(
        user_id: int = Depends(get_current_user_id),
        usecase: ChatUseCase = Depends(get_chat_usecase),
) -> None:
    """Удалить всю историю диалога текущего пользователя.

    Args:
        user_id: ID текущего пользователя из JWT.
        usecase: Usecase чата.
    """
    await usecase.clear_history(user_id=user_id)
