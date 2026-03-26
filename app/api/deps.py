"""Dependency Injection для FastAPI.

Предоставляет зависимости для получения сессии БД, репозиториев,
usecase-объектов и текущего пользователя по JWT.
"""

from typing import AsyncIterator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessageRepository
from app.repositories.users import UserRepository
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_session() -> AsyncIterator[AsyncSession]:
    """Создать и вернуть асинхронную сессию базы данных.

    Сессия автоматически закрывается после завершения запроса.
    """
    async with AsyncSessionLocal() as session:
        yield session


def get_user_repo(
        session: AsyncSession = Depends(get_session),
) -> UserRepository:
    """Создать репозиторий пользователей с текущей сессией."""
    return UserRepository(session)


def get_chat_repo(
        session: AsyncSession = Depends(get_session),
) -> ChatMessageRepository:
    """Создать репозиторий сообщений чата с текущей сессией."""
    return ChatMessageRepository(session)


def get_openrouter_client() -> OpenRouterClient:
    """Создать клиент для взаимодействия с OpenRouter."""
    return OpenRouterClient()


def get_auth_usecase(
        user_repo: UserRepository = Depends(get_user_repo),
) -> AuthUseCase:
    """Создать usecase аутентификации с репозиторием пользователей."""
    return AuthUseCase(user_repo)


def get_chat_usecase(
        chat_repo: ChatMessageRepository = Depends(get_chat_repo),
        openrouter_client: OpenRouterClient = Depends(get_openrouter_client),
) -> ChatUseCase:
    """Создать usecase чата с репозиторием сообщений и клиентом OpenRouter."""
    return ChatUseCase(chat_repo, openrouter_client)


async def get_current_user_id(
        token: str = Depends(oauth2_scheme),
) -> int:
    """Декодировать JWT и вернуть ID текущего пользователя.

    Raises:
        HTTPException: 401 если токен невалиден или истёк.
    """
    try:
        payload = decode_token(token)
        return int(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
