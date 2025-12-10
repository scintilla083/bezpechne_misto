from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext

from bot import texts
from bot.states import (
    MainMenuState,
    PoliceState,
    UtilityState,
    MayorState,
    FeedbackState,
    ChangeCityState,
    NarcotagsState
)
from bot.keyboards import (
    main_menu_keyboard,
    police_menu_keyboard,
    back_to_menu_keyboard,
    utility_menu_keyboard,
    collecting_keyboard,
    hromada_keyboard,
    BTN_BACK,
)
from bot.utils import (
    send_clean_message,
    track_user_message
)

main_menu_router = Router()


async def show_main_menu(bot: Bot, message: Message, state: FSMContext, with_photo: bool = False, delete_user_messages_flag: bool = False,):
    """
    Показать главное меню

    Args:
        bot: Экземпляр бота
        message: Сообщение пользователя
        state: FSM контекст
        with_photo: Показывать ли фото (только при первом показе)
        delete_user_messages_flag: delete previous message
    """
    await state.set_state(MainMenuState.main)

    # Показываем фото только при первом входе в меню
    photo = None
    if with_photo:
        try:
            photo = FSInputFile("bot/assets/main.jpg")
        except Exception:
            photo = None

    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.MAIN_MENU_TEXT,
        state=state,
        reply_markup=main_menu_keyboard(),
        photo=photo,
        delete_user_messages_flag=delete_user_messages_flag,
    )


@main_menu_router.message(MainMenuState.main, F.text == "Про сервіс")
async def about_bot(message: Message, state: FSMContext, bot: Bot):
    """Информация о сервисе"""
    await track_user_message(state, message.message_id)
    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.ABOUT_BOT_TEXT + "\n\n" + texts.MAIN_MENU_TEXT,
        state=state,
        reply_markup=main_menu_keyboard(),
        delete_user_messages_flag=True,
    )


@main_menu_router.message(MainMenuState.main, F.text == "Звернення до поліції")
async def menu_police(message: Message, state: FSMContext, bot: Bot):
    """Обращение в полицию"""
    await track_user_message(state, message.message_id)
    await state.set_state(PoliceState.choosing_category)
    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.POLICE_INTRO_TEXT,
        state=state,
        reply_markup=police_menu_keyboard(),
        delete_user_messages_flag=True,
    )


@main_menu_router.message(MainMenuState.main, F.text == "Звернення до комунального підприємства")
async def menu_utility(message: Message, state: FSMContext, bot: Bot):
    """Обращение в коммунальное предприятие"""
    # Очищаем данные предыдущего обращения
    await track_user_message(state, message.message_id)
    await state.update_data(appeal_id=None, messages_collected=0)
    await state.set_state(UtilityState.choosing_category)

    await send_clean_message(
        bot=bot,
        message=message,
        text="Оберіть категорію звернення:",
        state=state,
        reply_markup=utility_menu_keyboard(),
        delete_user_messages_flag=True,
    )


@main_menu_router.message(MainMenuState.main, F.text == "Звернення до міської ради")
async def menu_mayor(message: Message, state: FSMContext, bot: Bot):
    """Обращение в городской совет"""
    # Очищаем данные предыдущего обращения
    await track_user_message(state, message.message_id)
    await state.update_data(appeal_id=None, messages_collected=0)
    await state.set_state(MayorState.collecting)

    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.MAYOR_TEXT,
        state=state,
        reply_markup=back_to_menu_keyboard(),
        delete_user_messages_flag=True,
    )


@main_menu_router.message(MainMenuState.main, F.text == "Залишити відгук")
async def menu_feedback(message: Message, state: FSMContext, bot: Bot):
    """Оставить отзыв"""
    await track_user_message(state, message.message_id)
    await state.set_state(FeedbackState.collecting)
    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.FEEDBACK_INTRO_TEXT,
        state=state,
        reply_markup=back_to_menu_keyboard(),
        delete_user_messages_flag=True,
    )


@main_menu_router.message(MainMenuState.main, F.text == "Змінити населений пункт")
async def menu_change_city(message: Message, state: FSMContext, bot: Bot):
    await track_user_message(state, message.message_id)

    await state.set_state(ChangeCityState.waiting_for_hromada)

    await send_clean_message(
        bot=bot,
        message=message,
        text="Оберіть територіальну громаду Кам’янець-Подільського району:",
        state=state,
        reply_markup=hromada_keyboard(),
        delete_user_messages_flag=True,
    )


@main_menu_router.message(F.text == BTN_BACK)
async def go_back_to_main(message: Message, state: FSMContext, bot: Bot):
    """Возврат в главное меню из любого состояния"""
    # Очищаем данные
    await track_user_message(state, message.message_id)
    await state.update_data(appeal_id=None, messages_collected=0)
    await show_main_menu(
        bot=bot,
        message=message,
        state=state,
        with_photo=False,
        delete_user_messages_flag=True,  # <-- добавим такой параметр
    )

@main_menu_router.message(MainMenuState.main, F.text == "Наркотеги")
async def menu_narcotags(message: Message, state: FSMContext, bot: Bot):
    """Меню наркотегов (сбор ГЕО + фото)"""
    await track_user_message(state, message.message_id)

    await state.update_data(appeal_id=None, messages_collected=0)
    await state.set_state(NarcotagsState.collecting)

    await send_clean_message(
        bot=bot,
        message=message,
        text="Надішліть геолокацію та фото наркотегів. Можете також додати текст.\n\n"
             "Коли завершите — натисніть кнопку:",
        state=state,
        reply_markup=collecting_keyboard(),
        delete_user_messages_flag=True,
    )
