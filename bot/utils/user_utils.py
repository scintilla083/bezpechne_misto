"""
Утилиты для работы с пользователями
"""
from aiogram.types import Message
from apps.reports.models import TelegramUser


async def get_or_create_user(message: Message) -> TelegramUser:
    """
    Получить или создать пользователя из сообщения Telegram

    Args:
        message: Сообщение от пользователя

    Returns:
        TelegramUser: Объект пользователя
    """
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            "username": message.from_user.username,
            "full_name": message.from_user.full_name,
        },
    )

    # Обновляем информацию при каждом обращении
    if not created:
        updated = False
        if user.username != message.from_user.username:
            user.username = message.from_user.username
            updated = True
        if user.full_name != message.from_user.full_name:
            user.full_name = message.from_user.full_name
            updated = True
        if updated:
            user.save()

    return user