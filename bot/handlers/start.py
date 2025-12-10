from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot import texts
from bot.states import RegistrationState, MainMenuState
from bot.keyboards import main_menu_keyboard, phone_request_keyboard
from bot.utils import get_or_create_user, send_clean_message

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """Команда /start - начало работы с ботом"""
    # Получаем или создаем пользователя
    user = await get_or_create_user(message)

    await state.clear()

    # Приветствуем пользователя
    await message.answer(texts.WELCOME_TEXT)

    # Проверяем, нужна ли регистрация
    if not user.city or not user.phone_number:
        await send_clean_message(
            bot=bot,
            message=message,
            text=texts.ASK_CITY_TEXT,
            state=state,
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(RegistrationState.waiting_for_city)
    else:
        # Пользователь уже зарегистрирован
        await send_clean_message(
            bot=bot,
            message=message,
            text=texts.MAIN_MENU_TEXT,
            state=state,
            reply_markup=main_menu_keyboard(),
        )
        await state.set_state(MainMenuState.main)


@start_router.message(RegistrationState.waiting_for_city)
async def save_city(message: Message, state: FSMContext, bot: Bot):
    """Сохранение города пользователя"""
    user = await get_or_create_user(message)
    user.city = message.text.strip()
    user.save()

    # Переходим к запросу телефона
    await send_clean_message(
        bot=bot,
        message=message,
        text=texts.CITY_SAVED_TEXT + "\n\n" + texts.ASK_PHONE_TEXT,
        state=state,
        reply_markup=phone_request_keyboard(),
    )
    await state.set_state(RegistrationState.waiting_for_phone)


@start_router.message(RegistrationState.waiting_for_phone)
async def save_phone(message: Message, state: FSMContext, bot: Bot):
    """Сохранение номера телефона"""
    user = await get_or_create_user(message)

    # Получаем телефон из контакта или текста
    phone = None
    if message.contact and message.contact.phone_number:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text.strip()

    if phone:
        user.phone_number = phone
        user.save()

        # Регистрация завершена
        await send_clean_message(
            bot=bot,
            message=message,
            text=texts.REGISTRATION_COMPLETED_TEXT + "\n\n" + texts.MAIN_MENU_TEXT,
            state=state,
            reply_markup=main_menu_keyboard(),
        )
        await state.set_state(MainMenuState.main)
    else:
        # Если не получили телефон, просим еще раз
        await message.answer(
            "Будь ласка, надішліть номер телефону або скористайтесь кнопкою.",
            reply_markup=phone_request_keyboard(),
        )