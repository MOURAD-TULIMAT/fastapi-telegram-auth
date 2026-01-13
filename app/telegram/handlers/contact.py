from aiogram import Router
from aiogram.types import Message

from app.db.session import get_sessionmaker
from app.db import crud

router = Router()


@router.message(lambda m: m.contact is not None)
async def contact_handler(message: Message):
    contact = message.contact
    sender_id = message.from_user.id if message.from_user else None

    if sender_id is None:
        await message.answer("Unexpected error: missing sender info.")
        return

    # Ensure the user is sending their own contact card
    if contact.user_id is not None and contact.user_id != sender_id:
        await message.answer("Please send the phone number for this Telegram account.")
        return

    SessionLocal = get_sessionmaker()
    async with SessionLocal() as db:
        async with db.begin():
            user = await crud.activate_user_by_telegram_contact(
                db,
                telegram_user_id=str(sender_id),
                contact_phone_number=contact.phone_number or "",
            )

    if user is None:
        await message.answer(
            "Activation failed. Make sure you opened the activation link from the same Telegram account and sent the matching phone number."
        )
        return

    await message.answer("Your phone number has been confirmed. Your account is now activated.")
