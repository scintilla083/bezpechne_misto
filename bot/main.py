import os
import asyncio
import django
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "safe_city.settings")
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.handlers.start import start_router
from bot.handlers.main_menu import main_menu_router
from bot.handlers.police import police_router
from bot.handlers.utility import utility_router
from bot.handlers.mayor import mayor_router
from bot.handlers.feedback import feedback_router
from bot.handlers.change_city import change_city_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Запуск бота"""
    logger.info("Запуск бота...")

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем роутеры в правильном порядке
    dp.include_router(start_router)
    dp.include_router(main_menu_router)
    dp.include_router(police_router)
    dp.include_router(utility_router)
    dp.include_router(mayor_router)
    dp.include_router(feedback_router)
    dp.include_router(change_city_router)

    logger.info("Бот запущен и готов к работе")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")