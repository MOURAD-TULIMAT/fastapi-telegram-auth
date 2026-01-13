from aiogram import Bot, Dispatcher
from app.core.config import settings

def build_bot() -> Bot:
    return Bot(token=settings.TELEGRAM_BOT_TOKEN)

def build_dispatcher() -> Dispatcher:
    return Dispatcher()
