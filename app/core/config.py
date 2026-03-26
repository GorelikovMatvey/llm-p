"""Конфигурация приложения.

Читает переменные окружения из файла .env через pydantic-settings
и предоставляет единственный экземпляр Settings для импорта в других модулях.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения.

    Attributes:
        app_name: Название приложения.
        env: Окружение (local, staging, production).
        jwt_secret: Секретный ключ для подписи JWT.
        jwt_alg: Алгоритм подписи JWT (например, HS256).
        access_token_expire_minutes: Время жизни access token в минутах.
        sqlite_path: Путь к файлу базы данных SQLite.
        openrouter_api_key: API-ключ OpenRouter.
        openrouter_base_url: Базовый URL OpenRouter API.
        openrouter_model: Идентификатор используемой модели.
        openrouter_site_url: Referer-заголовок для запросов к OpenRouter.
        openrouter_app_name: Название приложения для заголовка X-Title.
    """

    # Приложение
    app_name: str
    env: str

    # JWT
    jwt_secret: str
    jwt_alg: str
    access_token_expire_minutes: int

    # База данных
    sqlite_path: str

    # OpenRouter
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    openrouter_site_url: str
    openrouter_app_name: str

    model_config = {"env_file": str(BASE_DIR / ".env")}


settings = Settings()
