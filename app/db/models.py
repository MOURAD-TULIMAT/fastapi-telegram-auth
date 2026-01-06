from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Unique + indexed phone
    phone_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)

    username: Mapped[str] = mapped_column(String(64), nullable=False)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)

    password_hash: Mapped[str | None] = mapped_column(String(256), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    telegram_user_id: Mapped[int | None] = mapped_column(String(32), nullable=True)

    created_at = mapped_column(DateTime(), default=utcnow, nullable=False)
    updated_at = mapped_column(DateTime(), default=utcnow, onupdate=utcnow, nullable=False)


    activation_tokens: Mapped[list["ActivationToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ActivationToken(Base):
    __tablename__ = "activation_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="activation_tokens")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="reset_tokens")
