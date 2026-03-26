"""Утилиты безопасности: хеширование паролей и работа с JWT.

Не обращается к базе данных и не знает об устройстве роутов.
Используется в usecases и слое dependency injection.
"""

import bcrypt as _bcrypt
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Фикс совместимости passlib с bcrypt >= 4.0
if not hasattr(_bcrypt, "__about__"):
    _bcrypt.__about__ = type("_About", (),
                             {"__version__": _bcrypt.__version__})()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Захешировать пароль с использованием bcrypt.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Хеш пароля.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль против его хеша.

    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хеш пароля из базы данных.

    Returns:
        True если пароль совпадает, False иначе.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, role: str) -> str:
    """Сгенерировать JWT access token.

    Payload содержит: sub (user_id), role, exp (время истечения),
    iat (время выдачи).

    Args:
        user_id: Идентификатор пользователя.
        role: Роль пользователя.

    Returns:
        Подписанный JWT токен.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_token(token: str) -> dict:
    """Декодировать и валидировать JWT токен.

    Проверяет подпись и срок действия токена.

    Args:
        token: JWT токен.

    Returns:
        Payload токена в виде словаря.

    Raises:
        ValueError: Если токен невалиден или истёк.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg],
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Невалидный токен: {e}")
