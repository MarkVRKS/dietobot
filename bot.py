import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, ADMIN_ID
from database.db import init_db, close_connection
from services.reminder_service import setup_scheduler, stop_scheduler
from handlers import start, profile, menu, weight, calories, reminders, admin, water, articles, statistics, referral

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN не установлен! Установите переменную окружения BOT_TOKEN.")
        return

    await init_db()
    logger.info("База данных инициализирована")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(menu.router)
    dp.include_router(weight.router)
    dp.include_router(calories.router)
    dp.include_router(reminders.router)
    dp.include_router(water.router)
    dp.include_router(articles.router)
    dp.include_router(statistics.router)
    dp.include_router(referral.router)
    dp.include_router(admin.router)

    setup_scheduler()
    logger.info("Планировщик запущ")

    logger.info("Бот запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        stop_scheduler()
        await close_connection()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
