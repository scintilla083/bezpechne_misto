from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot import texts

from bot.states import ChangeCityState, MainMenuState
from bot.keyboards import village_keyboard, hromada_keyboard, main_menu_keyboard
from bot.utils import send_clean_message, track_user_message
from bot.data.hromadas import HROMADAS
from apps.reports.models import TelegramUser

change_city_router = Router()

@change_city_router.message(ChangeCityState.waiting_for_hromada)
async def select_hromada(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    hromada_name = message.text

    if hromada_name not in HROMADAS:
        return await message.answer(
            "Будь ласка, оберіть громаду зі списку.",
            reply_markup=hromada_keyboard()
        )

    await state.update_data(selected_hromada=hromada_name)
    await state.set_state(ChangeCityState.waiting_for_village)

    await send_clean_message(
        bot=bot,
        message=message,
        text=f"Оберіть населений пункт у громаді:\n<b>{hromada_name}</b>",
        state=state,
        reply_markup=village_keyboard(hromada_name),
        delete_user_messages_flag=True,
    )


@change_city_router.message(ChangeCityState.waiting_for_village)
async def select_village(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    hromada = data.get("selected_hromada")
    village = message.text

    if village == "⬅️ Назад до громад":
        await state.set_state(ChangeCityState.waiting_for_hromada)
        return await message.answer(
            "Оберіть територіальну громаду:",
            reply_markup=hromada_keyboard()
        )

    if village not in HROMADAS.get(hromada, []):
        return await message.answer(
            "Будь ласка, оберіть населений пункт зі списку.",
            reply_markup=village_keyboard(hromada)
        )

    # Сохраняем населённый пункт пользователю
    tg_id = message.from_user.id
    user = TelegramUser.objects.get(telegram_id=tg_id)
    user.city = village
    user.save()

    await state.set_state(MainMenuState.main)

    await send_clean_message(
        bot=bot,
        message=message,
        text=f"Ваш населений пункт успішно змінено на:\n<b>{village}</b>\n\n{texts.MAIN_MENU_TEXT}",
        state=state,
        reply_markup=main_menu_keyboard(),
        delete_user_messages_flag=True,
    )
