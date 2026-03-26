"""Эндпоинты аутентификации и управления профилем.

Маршруты:
    POST /auth/register — регистрация нового пользователя.
    POST /auth/login    — вход и получение JWT access token.
    GET  /auth/me       — профиль текущего авторизованного пользователя.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_usecase, get_current_user_id
from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register(
        body: RegisterRequest,
        usecase: AuthUseCase = Depends(get_auth_usecase),
) -> UserPublic:
    """Зарегистрировать нового пользователя.

    Args:
        body: Email и пароль нового пользователя.
        usecase: Usecase аутентификации.

    Returns:
        Публичные данные созданного пользователя.

    Raises:
        HTTPException: 409 если пользователь с таким email уже существует.
    """
    try:
        user = await usecase.register(email=body.email, password=body.password)
        return user
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
)
async def login(
        form: OAuth2PasswordRequestForm = Depends(),
        usecase: AuthUseCase = Depends(get_auth_usecase),
) -> TokenResponse:
    """Выполнить вход и получить JWT access token.

    Принимает форму OAuth2 — поле username используется как email.

    Args:
        form: Форма с username (email) и password.
        usecase: Usecase аутентификации.

    Returns:
        JWT access token с типом bearer.

    Raises:
        HTTPException: 401 если email не найден или пароль неверный.
    """
    try:
        token = await usecase.login(email=form.username,
                                    password=form.password)
        return TokenResponse(access_token=token)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Профиль текущего пользователя",
)
async def get_me(
        user_id: int = Depends(get_current_user_id),
        usecase: AuthUseCase = Depends(get_auth_usecase),
) -> UserPublic:
    """Вернуть профиль авторизованного пользователя.

    Args:
        user_id: ID пользователя из JWT токена.
        usecase: Usecase аутентификации.

    Returns:
        Публичные данные текущего пользователя.

    Raises:
        HTTPException: 404 если пользователь не найден.
    """
    try:
        return await usecase.get_profile(user_id=user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(e))
