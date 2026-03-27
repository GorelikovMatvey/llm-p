"""Pydantic-схемы пользователя.

Содержит публичное представление пользователя для ответов API.
Поля password и password_hash намеренно исключены.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserPublic(BaseModel):
    """Публичные данные пользователя, возвращаемые в ответах API.

    Attributes:
        id: Уникальный идентификатор пользователя.
        email: Email пользователя.
        role: Роль пользователя в системе.
        created_at: Дата и время регистрации в UTC.
    """

    id: int
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
