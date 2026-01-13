from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.core.config import settings
from app.db.session import get_sessionmaker
from app.db import crud

router = Router()


def register_url() -> str:
    return settings.WEB_APP_BASE_URL.rstrip("/") + settings.WEB_APP_REGISTER_PATH


def retry_url() -> str:
    return settings.WEB_APP_BASE_URL.rstrip("/") + settings.WEB_APP_RETRY_ACTIVATION_PATH


@router.message(CommandStart())
async def start(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    token = parts[1].strip() if len(parts) > 1 else None

    if not token:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Register", url=register_url())],
            ]
        )
        await message.answer(
            "Welcome. Please register to activate your phone number.",
            reply_markup=kb,
        )
        return

    sender_id = str(message.from_user.id)

    SessionLocal = get_sessionmaker()
    async with SessionLocal() as db:
        async with db.begin():
            ok = await crud.bind_telegram_user_for_activation(
                db,
                raw_token=token,
                telegram_user_id=sender_id,
            )

    if not ok:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Register", url=register_url())],
                [InlineKeyboardButton(text="Retry activation", url=retry_url())],
            ]
        )
        await message.answer("Invalid or expired activation link.", reply_markup=kb)
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Send my phone number", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await message.answer(
        "To confirm, please send your Telegram phone number contact card.",
        reply_markup=kb,
    )
