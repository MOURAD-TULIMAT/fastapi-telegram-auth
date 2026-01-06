from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.phone import normalize_phone
from app.core.tokens import new_raw_token, token_hash
from app.db.models import User, ActivationToken

def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def activation_expiry() -> datetime:
    return now_utc() + timedelta(minutes=settings.ACTIVATION_TOKEN_TTL_MINUTES)


async def get_user_by_phone(session: AsyncSession, phone_number: str) -> User | None:
    phone_number = normalize_phone(phone_number)
    res = await session.execute(select(User).where(User.phone_number == phone_number))
    return res.scalar_one_or_none()


async def upsert_inactive_user_for_registration(
    session: AsyncSession,
    *,
    phone_number: str,
    username: str,
    first_name: str,
    last_name: str,
    email: str | None,
) -> User:
    phone_number = normalize_phone(phone_number)
    user = await get_user_by_phone(session, phone_number)

    if user is None:
        user = User(
            phone_number=phone_number,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=False,
        )
        session.add(user)
        return user

    if user.is_active:
        raise ValueError("USER_ALREADY_ACTIVE")

    # overwrite only if old enough
    if user.updated_at and (now_utc() - user.updated_at).total_seconds() <= settings.INACTIVE_OVERWRITE_AFTER_SECONDS:
        raise ValueError("REGISTRATION_RECENTLY_CREATED")

    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.email = email

    # remove old activation tokens
    await session.execute(delete(ActivationToken).where(ActivationToken.user_id == user.id))
    return user


async def create_activation_token(session: AsyncSession, user_id: str) -> ActivationToken:
    token = new_raw_token()
    at = ActivationToken(
        token_hash=token_hash(token),
        user_id=user_id,
        expires_at=activation_expiry(),
        consumed_at=None,
    )
    session.add(at)
    return at, token
