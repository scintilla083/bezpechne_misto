from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import NarcotagsState, MainMenuState
from bot.keyboards import collecting_keyboard, confirm_inline_keyboard, main_menu_keyboard
from bot.utils import create_or_update_appeal, collect_appeal_data, finalize_appeal, send_clean_message, track_user_message
from apps.reports.models import Appeal

narcotags_router = Router()


@narcotags_router.message(NarcotagsState.collecting, F.text == "✅ Завершити збір інформації")
async def narcotags_finish(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    data = await state.get_data()
    appeal_id = data.get("appeal_id")

    if not appeal_id:
        await send_clean_message(
            bot=bot,
            message=message,
            text="Помилка. Звернення не знайдено.",
            state=state,
            reply_markup=main_menu_keyboard(),
            delete_user_messages_flag=True,
        )
        await state.set_state(MainMenuState.main)
        return

    appeal = Appeal.objects.get(id=appeal_id)

    if not appeal.media.exists() and not appeal.latitude:
        return await message.answer(
            "Будь ласка, надішліть хоча б фото або геолокацію.",
            reply_markup=collecting_keyboard(),
        )

    await state.set_state(NarcotagsState.confirming)

    await send_clean_message(
        bot=bot,
        message=message,
        text="Підтвердити відправку інформації?",
        state=state,
        reply_markup=confirm_inline_keyboard(),
        delete_user_messages_flag=False,
    )


@narcotags_router.message(NarcotagsState.collecting)
async def narcotags_collect(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    appeal = await create_or_update_appeal(
        message=message,
        state=state,
        target=Appeal.Target.NARCOTAGS,    # или создать новый target "narcotags"
    )

    collected = await collect_appeal_data(message, appeal, state)

    msg_count = (await state.get_data()).get("messages_collected", 0)

    status = []
    if collected["media"]:
        status.append("📸 Фото отримано")
    if collected["location"]:
        status.append("📍 Локація отримана")
    if collected["text"]:
        status.append("✏️ Текст додано")

    await send_clean_message(
        bot=bot,
        message=message,
        text=f"Прийнято ({msg_count})\n" + "\n".join(status),
        state=state,
        reply_markup=collecting_keyboard(),
        delete_user_messages_flag=False,
    )


@narcotags_router.callback_query(NarcotagsState.confirming, F.data == "confirm_yes")
async def narcotags_confirm_yes(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    appeal = Appeal.objects.get(id=(await state.get_data()).get("appeal_id"))
    await finalize_appeal(appeal)

    await state.set_state(MainMenuState.main)

    await send_clean_message(
        bot=bot,
        message=callback.message,
        text="Дякуємо! Інформацію передано.\n\n" + "Головне меню:",
        state=state,
        reply_markup=main_menu_keyboard(),
        delete_user_messages_flag=True,
    )


@narcotags_router.callback_query(NarcotagsState.confirming, F.data == "confirm_no")
async def narcotags_confirm_no(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    await state.set_state(MainMenuState.main)

    await send_clean_message(
        bot=bot,
        message=callback.message,
        text="Скасовано.\n\nГоловне меню:",
        state=state,
        reply_markup=main_menu_keyboard(),
        delete_user_messages_flag=True,
    )
