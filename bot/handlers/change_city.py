from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot import texts
from bot.states import ChangeCityState, MainMenuState
from bot.keyboards import main_menu_keyboard
from bot.utils import get_or_create_user, send_clean_message

change_city_router = Router()

# TODO добавить валидацию городов и не давать пользователем писать случайный текст
@change_city_router.message(ChangeCityState.waiting_for_city)
async def change_city(message: Message, state: FSMContext, bot: Bot):
    """Изменение города"""
    user = await get_or_create_user(message)
    user.city = message.text.strip()
    user.save()

    await state.set_state(MainMenuState.main)
    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.CHANGE_CITY_DONE_TEXT + "\n\n" + texts.MAIN_MENU_TEXT,
        state=state,
        reply_markup=main_menu_keyboard(),
    )