"""Бизнес-логика аутентификации и управления профилем.

Не содержит HTTPException и не зависит от FastAPI.
Все ошибки выбрасываются как доменные исключения из app.core.errors.
"""

from app.core.errors import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, hash_password, \
    verify_password
from app.db.models import User
from app.repositories.users import UserRepository


class AuthUseCase:
    """Usecase для регистрации, логина и получения профиля пользователя.

    Attributes:
        _user_repo: Репозиторий пользователей.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        """Инициализировать usecase с репозиторием пользователей.

        Args:
            user_repo: Репозиторий для работы с таблицей users.
        """
        self._user_repo = user_repo

    async def register(self, email: str, password: str) -> User:
        """Зарегистрировать нового пользователя.

        Проверяет уникальность email, хеширует пароль
        и создаёт пользователя через репозиторий.

        Args:
            email: Email нового пользователя.
            password: Пароль в открытом виде.

        Returns:
            Созданный ORM-объект пользователя.

        Raises:
            ConflictError: Если пользователь с таким email уже существует.
        """
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise ConflictError(f"Email {email} уже зарегистрирован")

        password_hash = hash_password(password)
        return await self._user_repo.create(email=email,
                                            password_hash=password_hash)

    async def login(self, email: str, password: str) -> str:
        """Выполнить вход и выдать JWT access token.

        Находит пользователя по email и проверяет пароль.
        При успехе генерирует и возвращает JWT токен.

        Args:
            email: Email пользователя.
            password: Пароль в открытом виде.

        Returns:
            Подписанный JWT access token.

        Raises:
            UnauthorizedError: Если email не найден или пароль неверный.
        """
        user = await self._user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Неверный email или пароль")

        return create_access_token(user_id=user.id, role=user.role)

    async def get_profile(self, user_id: int) -> User:
        """Получить профиль пользователя по ID.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            ORM-объект пользователя.

        Raises:
            NotFoundError: Если пользователь с указанным ID не найден.
        """
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"Пользователь с id={user_id} не найден")
        return user
