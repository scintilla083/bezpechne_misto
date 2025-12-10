from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot import texts
from bot.states import UtilityState, MainMenuState
from bot.keyboards import (
    collecting_keyboard,
    confirm_inline_keyboard,
    main_menu_keyboard,
)
from bot.utils import (
    create_or_update_appeal,
    collect_appeal_data,
    finalize_appeal,
    send_clean_message,
    track_user_message,
)
from apps.reports.models import Appeal

utility_router = Router()


@utility_router.message(UtilityState.collecting, F.text == "✅ Завершити збір інформації")
async def finish_collecting_utility(message: Message, state: FSMContext, bot: Bot):
    """Завершение сбора информации"""
    # Отслеживаем сообщение пользователя
    await track_user_message(state, message.message_id)

    data = await state.get_data()
    appeal_id = data.get("appeal_id")

    if not appeal_id:
        await send_clean_message(
            bot=bot,
            message=message,
            text=texts.ERROR_NO_APPEAL_TEXT,
            state=state,
            reply_markup=main_menu_keyboard(),
            delete_user_messages_flag=True,
        )
        await state.set_state(MainMenuState.main)
        return

    try:
        appeal = Appeal.objects.get(id=appeal_id)

        # Проверяем, есть ли данные
        if not appeal.text.strip():
            await message.answer(
                "Будь ласка, спочатку надішліть інформацію про проблему.",
                reply_markup=collecting_keyboard(),
            )
            return

        # Показываем подтверждение (НЕ удаляем сообщения пользователя)
        await state.set_state(UtilityState.confirming)
        await send_clean_message(
            bot=bot,
            message=message,
            text=texts.CONFIRM_FINISH_TEXT,
            state=state,
            reply_markup=confirm_inline_keyboard(),
            delete_user_messages_flag=False,  # НЕ удаляем - пользователь должен видеть свои данные
        )

    except Appeal.DoesNotExist:
        await send_clean_message(
            bot=bot,
            message=message,
            text=texts.ERROR_NO_APPEAL_TEXT,
            state=state,
            reply_markup=main_menu_keyboard(),
            delete_user_messages_flag=True,
        )
        await state.set_state(MainMenuState.main)


@utility_router.message(UtilityState.collecting)
async def collect_utility(message: Message, state: FSMContext, bot: Bot):
    """Сбор данных для обращения в коммунальное предприятие"""
    # Отслеживаем ВСЕ сообщения пользователя
    await track_user_message(state, message.message_id)

    # Создаем или получаем обращение
    appeal = await create_or_update_appeal(
        message=message,
        state=state,
        target=Appeal.Target.UTILITY,
    )

    # Собираем данные
    collected = await collect_appeal_data(message, appeal, state)

    # Формируем статус
    status_parts = []
    if collected["text"]:
        status_parts.append("✅ Текст")
    if collected["media"]:
        status_parts.append("✅ Медіа")
    if collected["location"]:
        status_parts.append("✅ Локація")

    status = " | ".join(status_parts) if status_parts else "⏳"

    data = await state.get_data()
    msg_count = data.get("messages_collected", 0)

    response_text = (
        f"Прийнято ✅ (Повідомлення: {msg_count})\n\n"
        f"{status}\n\n"
        f"Можете надіслати ще інформацію або натисніть кнопку завершення."
    )

    # НЕ удаляем сообщения пользователя
    await send_clean_message(
        bot=bot,
        message=message,
        text=response_text,
        state=state,
        reply_markup=collecting_keyboard(),
        delete_user_messages_flag=False,
    )


@utility_router.callback_query(UtilityState.confirming, F.data == "confirm_yes")
async def confirm_utility_yes(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Подтверждение обращения - удаляем все сообщения"""
    await callback.answer()

    data = await state.get_data()
    appeal_id = data.get("appeal_id")

    if appeal_id:
        try:
            appeal = Appeal.objects.get(id=appeal_id)
            await finalize_appeal(appeal)
        except Appeal.DoesNotExist:
            pass

    await state.set_state(MainMenuState.main)

    # УДАЛЯЕМ ВСЕ сообщения после подтверждения
    await send_clean_message(
        bot=bot,
        message=callback.message,
        text=texts.THANK_YOU_TEXT + "\n\n" + texts.MAIN_MENU_TEXT,
        state=state,
        reply_markup=main_menu_keyboard(),
        delete_user_messages_flag=True,  # ✅ УДАЛЯЕМ сообщения пользователя
    )


@utility_router.callback_query(UtilityState.confirming, F.data == "confirm_no")
async def confirm_utility_no(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Отмена подтверждения - удаляем всё"""
    await callback.answer()

    await state.set_state(MainMenuState.main)

    # При отмене также удаляем всё
    await send_clean_message(
        bot=bot,
        message=callback.message,
        text=texts.MAIN_MENU_TEXT,
        state=state,
        reply_markup=main_menu_keyboard(),
        delete_user_messages_flag=True,  # ✅ УДАЛЯЕМ сообщения пользователя
    )


@utility_router.message(UtilityState.choosing_category, F.text == "Переповнений смітник")
async def choose_trash_overflow(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    await create_or_update_appeal(
        message=message,
        state=state,
        target=Appeal.Target.UTILITY,
        utility_category=Appeal.UtilityCategory.TRASH_OVERFLOW
    )

    await state.set_state(UtilityState.collecting)

    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.UTILITY_TEXT,
        state=state,
        reply_markup=collecting_keyboard(),
    )


@utility_router.message(UtilityState.choosing_category, F.text == "Наслідки негоди")
async def choose_weather_damage(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    await create_or_update_appeal(
        message=message,
        state=state,
        target=Appeal.Target.UTILITY,
        utility_category=Appeal.UtilityCategory.WEATHER_DAMAGE
    )

    await state.set_state(UtilityState.collecting)

    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.UTILITY_TEXT,
        state=state,
        reply_markup=collecting_keyboard(),
    )
@utility_router.message(UtilityState.choosing_category, F.text == "Зачинене бомбосховище")
async def choose_shelter_closed(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    await create_or_update_appeal(
        message=message,
        state=state,
        target=Appeal.Target.UTILITY,
        utility_category=Appeal.UtilityCategory.SHELTER_CLOSED
    )

    await state.set_state(UtilityState.collecting)

    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.UTILITY_TEXT,
        state=state,
        reply_markup=collecting_keyboard(),
    )

@utility_router.message(UtilityState.choosing_category, F.text == "Засмічення")
async def choose_littering(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    await create_or_update_appeal(
        message=message,
        state=state,
        target=Appeal.Target.UTILITY,
        utility_category=Appeal.UtilityCategory.LITTERING
    )

    await state.set_state(UtilityState.collecting)

    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.UTILITY_TEXT,
        state=state,
        reply_markup=collecting_keyboard(),
    )

@utility_router.message(UtilityState.choosing_category, F.text == "Інший випадок")
async def choose_other_utility(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    await create_or_update_appeal(
        message=message,
        state=state,
        target=Appeal.Target.UTILITY,
        utility_category=Appeal.UtilityCategory.OTHER
    )

    await state.set_state(UtilityState.collecting)

    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.UTILITY_TEXT,
        state=state,
        reply_markup=collecting_keyboard(),
    )
