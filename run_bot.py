import asyncio
from aiogram import Dispatcher
from app.telegram.bot import build_bot, build_dispatcher
from app.telegram.handlers import start, contact

async def main():
    bot = build_bot()
    dp: Dispatcher = build_dispatcher()
    dp.include_router(start.router)
    dp.include_router(contact.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
