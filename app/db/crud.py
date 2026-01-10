from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.phone import normalize_phone
from app.core.tokens import new_raw_token, token_hash
from app.db.models import User, ActivationToken

def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def activation_expiry(now: datetime) -> datetime:
    return now + timedelta(minutes=settings.ACTIVATION_TOKEN_TTL_MINUTES)

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


async def create_activation_token(session: AsyncSession, user_id: str) -> tuple[str, datetime]:
    raw = new_raw_token()
    now = now_utc()
    exp = activation_expiry(now)

    row = ActivationToken(
        token_hash=token_hash(raw),
        user_id=user_id,
        expires_at=exp,
        consumed_at=None,
    )
    session.add(row)
    return raw, exp


async def retry_activation_token_by_phone(session: AsyncSession, phone_number: str) -> tuple[User, str, datetime]:
    phone = normalize_phone(phone_number)

    res = await session.execute(select(User).where(User.phone_number == phone))
    user = res.scalar_one_or_none()
    if user is None or user.is_active:
        raise ValueError("USER_NOT_FOUND_OR_ACTIVE")

    # Keep a single usable activation token per user
    await session.execute(delete(ActivationToken).where(ActivationToken.user_id == user.id))

    raw, exp = await create_activation_token(session, user.id)
    return user, raw, exp

async def get_valid_activation_token(session: AsyncSession, raw_token: str) -> ActivationToken | None:
    h = token_hash(raw_token)
    res = await session.execute(
        select(ActivationToken).where(ActivationToken.token_hash == h)
    )
    tok = res.scalar_one_or_none()
    if tok is None:
        return None
    if tok.consumed_at is not None:
        return None
    if tok.expires_at <= now_utc():
        return None
    return tok

async def consume_activation_and_activate_user(session: AsyncSession, *, raw_token: str, telegram_user_id: str) -> User | None:
    tok = await get_valid_activation_token(session, raw_token)
    if tok is None:
        return None

    # Load user
    res = await session.execute(select(User).where(User.id == tok.user_id))
    user = res.scalar_one()

    # Activate + bind telegram user id
    user.is_active = True
    user.telegram_user_id = telegram_user_id

    # Consume token
    tok.consumed_at = now_utc()

    return user