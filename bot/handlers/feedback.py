from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot import texts
from bot.states import FeedbackState, MainMenuState
from bot.keyboards import main_menu_keyboard
from bot.utils import get_or_create_user, send_clean_message
from apps.reports.models import Appeal

feedback_router = Router()


@feedback_router.message(FeedbackState.collecting)
async def collect_feedback(message: Message, state: FSMContext, bot: Bot):
    """Сбор отзыва"""
    user = await get_or_create_user(message)

    # Создаем обращение типа отзыв
    Appeal.objects.create(
        user=user,
        target=Appeal.Target.FEEDBACK,
        text=message.text or message.caption or "",
        is_submitted=True,
    )

    await state.set_state(MainMenuState.main)
    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.FEEDBACK_THANKS_TEXT + "\n\n" + texts.MAIN_MENU_TEXT,
        state=state,
        reply_markup=main_menu_keyboard(),
    )