"""
Утилиты для работы с обращениями (Appeals)
"""
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from apps.reports.models import Appeal, TelegramUser
from apps.reports.services import save_media_from_message
from .user_utils import get_or_create_user


async def create_or_update_appeal(
        message: Message,
        state: FSMContext,
        target: str,
        police_category: str = None,
) -> Appeal:
    """
    Создать новое обращение или получить существующее из state

    Args:
        message: Сообщение пользователя
        state: FSM контекст
        target: Цель обращения (POLICE, UTILITY, MAYOR, FEEDBACK)
        police_category: Категория для полиции (опционально)

    Returns:
        Appeal: Объект обращения
    """
    data = await state.get_data()
    appeal_id = data.get("appeal_id")

    if appeal_id:
        try:
            appeal = Appeal.objects.get(id=appeal_id)
            return appeal
        except Appeal.DoesNotExist:
            pass

    # Создаем новое обращение
    user = await get_or_create_user(message)

    appeal_data = {
        "user": user,
        "target": target,
        "text": "",
    }

    if police_category:
        appeal_data["police_category"] = police_category

    appeal = Appeal.objects.create(**appeal_data)
    await state.update_data(appeal_id=appeal.id, messages_collected=0)

    return appeal


async def collect_appeal_data(message: Message, appeal: Appeal, state: FSMContext) -> dict:
    """
    Собрать данные из сообщения и добавить к обращению

    Args:
        message: Сообщение пользователя
        appeal: Объект обращения
        state: FSM контекст для отслеживания прогресса

    Returns:
        dict: Информация о собранных данных
    """
    collected = {
        "text": False,
        "media": False,
        "location": False,
    }

    # Собираем текст из сообщения и подписи
    text_parts = []
    if message.text:
        text_parts.append(message.text)
    if message.caption:
        text_parts.append(message.caption)

    if text_parts:
        new_text = "\n\n".join(text_parts)
        if appeal.text:
            appeal.text += "\n\n" + new_text
        else:
            appeal.text = new_text
        collected["text"] = True

    # Собираем локацию
    if message.location:
        appeal.latitude = message.location.latitude
        appeal.longitude = message.location.longitude
        if not appeal.location_text:
            appeal.location_text = f"{appeal.latitude}, {appeal.longitude}"
        collected["location"] = True

    # Собираем медиа (фото, видео, документы)
    media_saved = await save_media_from_message(message, appeal)
    if media_saved:
        collected["media"] = True

    appeal.save()

    # Обновляем счетчик собранных сообщений
    data = await state.get_data()
    messages_count = data.get("messages_collected", 0) + 1
    await state.update_data(messages_collected=messages_count)

    return collected


async def finalize_appeal(appeal: Appeal) -> None:
    """
    Финализировать обращение перед отправкой
    Добавляет город пользователя к локации, если локация не указана

    Args:
        appeal: Объект обращения
    """
    # Если нет текстовой локации, но есть город пользователя
    if not appeal.location_text and appeal.user.city:
        if appeal.latitude and appeal.longitude:
            appeal.location_text = (
                f"{appeal.user.city} ({appeal.latitude:.5f}, {appeal.longitude:.5f})"
            )
        else:
            appeal.location_text = appeal.user.city

    appeal.is_submitted = True
    appeal.save()


def get_collected_data_summary(collected: dict) -> str:
    """
    Получить текстовое описание собранных данных

    Args:
        collected: Словарь с флагами собранных данных

    Returns:
        str: Текстовое описание
    """
    items = []
    if collected.get("text"):
        items.append("✅ Текст")
    if collected.get("media"):
        items.append("✅ Медіа")
    if collected.get("location"):
        items.append("✅ Локація")

    return " | ".join(items) if items else "⏳ Очікую дані"