"""Pydantic-схемы для аутентификации.

Используются в эндпоинтах регистрации и логина.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Данные для регистрации нового пользователя.

    Attributes:
        email: Email пользователя в корректном формате.
        password: Пароль длиной от 8 до 64 символов.
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "student_surname@email.com",
                 "password": "strongpassword123"}
            ]
        }
    }


class TokenResponse(BaseModel):
    """Ответ с JWT access token.

    Attributes:
        access_token: Подписанный JWT токен.
        token_type: Тип токена, всегда "bearer".
    """

    access_token: str
    token_type: str = "bearer"
