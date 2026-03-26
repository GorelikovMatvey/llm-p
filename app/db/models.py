"""ORM-модели базы данных.

Содержит описание таблиц users и chat_messages.
Файл не содержит бизнес-логики — только структуру данных
и связи между таблицами.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    """Модель пользователя.

    Attributes:
        id: Первичный ключ, автоинкремент.
        email: Уникальный email пользователя, индексирован.
        password_hash: Хеш пароля, вычисленный через bcrypt.
        role: Роль пользователя (по умолчанию "user").
        created_at: Дата и время регистрации в UTC.
        messages: Связь с сообщениями чата пользователя.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False,
                                       index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    """Модель сообщения чата.

    Хранит отдельные сообщения диалога пользователя с LLM.
    Каждое сообщение привязано к конкретному пользователю
    и имеет роль: "user" (запрос) или "assistant" (ответ модели).

    Attributes:
        id: Первичный ключ, автоинкремент.
        user_id: Внешний ключ на таблицу users.
        role: Роль отправителя — "user" или "assistant".
        content: Текст сообщения.
        created_at: Дата и время создания сообщения в UTC.
        user: Обратная связь с моделью пользователя.
    """

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="messages"
    )

    __table_args__ = (
        Index("ix_chat_messages_user_id", "user_id"),
    )
