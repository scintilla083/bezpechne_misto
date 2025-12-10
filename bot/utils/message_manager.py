"""
Управление сообщениями бота для поддержания чистоты чата
"""
from typing import Optional, List
from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import logging

logger = logging.getLogger(__name__)


async def delete_bot_messages(bot: Bot, state: FSMContext, chat_id: int) -> None:
    """
    Удалить предыдущие сообщения бота для чистоты интерфейса

    Args:
        bot: Экземпляр бота
        state: FSM контекст
        chat_id: ID чата
    """
    data = await state.get_data()
    message_ids = data.get("bot_message_ids", [])

    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except TelegramBadRequest as e:
            logger.warning(f"Не удалось удалить сообщение {msg_id}: {e}")

    # Очищаем список после удаления
    await state.update_data(bot_message_ids=[])


async def delete_user_messages(bot: Bot, state: FSMContext, chat_id: int) -> None:
    """
    Удалить сообщения пользователя для чистоты интерфейса

    Args:
        bot: Экземпляр бота
        state: FSM контекст
        chat_id: ID чата
    """
    data = await state.get_data()
    message_ids = data.get("user_message_ids", [])

    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except TelegramBadRequest as e:
            logger.warning(f"Не удалось удалить сообщение пользователя {msg_id}: {e}")

    # Очищаем список после удаления
    await state.update_data(user_message_ids=[])


async def delete_all_messages(bot: Bot, state: FSMContext, chat_id: int) -> None:
    """
    Удалить ВСЕ сообщения (бота и пользователя) для полной очистки

    Args:
        bot: Экземпляр бота
        state: FSM контекст
        chat_id: ID чата
    """
    await delete_bot_messages(bot, state, chat_id)
    await delete_user_messages(bot, state, chat_id)


async def track_user_message(state: FSMContext, message_id: int) -> None:
    """
    Добавить ID сообщения пользователя для последующего удаления

    Args:
        state: FSM контекст
        message_id: ID сообщения пользователя
    """
    data = await state.get_data()
    message_ids = data.get("user_message_ids", [])
    message_ids.append(message_id)
    await state.update_data(user_message_ids=message_ids)


async def send_clean_message(
    bot: Bot,
    message: Message,
    text: str,
    state: FSMContext,
    reply_markup: Optional[ReplyKeyboardMarkup | InlineKeyboardMarkup] = None,
    photo: Optional[FSInputFile | str] = None,
    delete_user_messages_flag: bool = False,
) -> Message:
    """
    Отправить сообщение с предварительным удалением старых сообщений бота

    Args:
        bot: Экземпляр бота
        message: Сообщение пользователя
        text: Текст для отправки
        state: FSM контекст
        reply_markup: Клавиатура (опционально)
        photo: Фото для отправки (опционально)
        delete_user_messages: Удалять ли также сообщения пользователя

    Returns:
        Message: Отправленное сообщение
    """
    # Удаляем старые сообщения бота
    await delete_bot_messages(bot, state, message.chat.id)

    # Удаляем сообщения пользователя, если нужно (после подтверждения)
    if delete_user_messages_flag:
        await delete_user_messages(bot, state, message.chat.id)

    # Отправляем новое сообщение
    if photo:
        try:
            sent_msg = await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=reply_markup,
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить фото: {e}. Отправляю текст.")
            sent_msg = await message.answer(text, reply_markup=reply_markup)
    else:
        sent_msg = await message.answer(text, reply_markup=reply_markup)

    # Сохраняем ID отправленного сообщения
    data = await state.get_data()
    message_ids = data.get("bot_message_ids", [])
    message_ids.append(sent_msg.message_id)
    await state.update_data(bot_message_ids=message_ids)

    return sent_msg


async def edit_last_message(
    bot: Bot,
    chat_id: int,
    text: str,
    state: FSMContext,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> Optional[Message]:
    """
    Отредактировать последнее сообщение бота или отправить новое

    Args:
        bot: Экземпляр бота
        chat_id: ID чата
        text: Новый текст
        state: FSM контекст
        reply_markup: Inline клавиатура (опционально)

    Returns:
        Message: Отредактированное сообщение или None
    """
    data = await state.get_data()
    message_ids = data.get("bot_message_ids", [])

    if not message_ids:
        return None

    last_message_id = message_ids[-1]

    try:
        edited_msg = await bot.edit_message_text(
            chat_id=chat_id,
            message_id=last_message_id,
            text=text,
            reply_markup=reply_markup,
        )
        return edited_msg
    except TelegramBadRequest as e:
        logger.warning(f"Не удалось отредактировать сообщение {last_message_id}: {e}")
        return None


async def add_bot_message_id(state: FSMContext, message_id: int) -> None:
    """
    Добавить ID сообщения бота в список для последующего удаления

    Args:
        state: FSM контекст
        message_id: ID сообщения
    """
    data = await state.get_data()
    message_ids = data.get("bot_message_ids", [])
    message_ids.append(message_id)
    await state.update_data(bot_message_ids=message_ids)