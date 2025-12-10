from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

BTN_BACK = "⬅️ Повернутися до головного меню"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Звернення до поліції"),
                KeyboardButton(text="Звернення до комунального підприємства"),
            ],
            [
                KeyboardButton(text="Звернення до міської ради"),
                KeyboardButton(text="Наркотеги"),
                KeyboardButton(text="Про сервіс"),
            ],
            [
                KeyboardButton(text="Залишити відгук"),
                KeyboardButton(text="Змінити населений пункт"),
            ],
        ],
        resize_keyboard=True,
    )


def police_menu_keyboard() -> ReplyKeyboardMarkup:
    """Меню выбора категории обращения в полицию"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ДТП")],
            [KeyboardButton(text="Розпиття")],
            [KeyboardButton(text="Порушення громадського порядку")],
            [KeyboardButton(text="Неправильна парковка")],
            [KeyboardButton(text="Інше порушення")],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def collecting_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура во время сбора информации"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Завершити збір інформації")],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )


def confirm_inline_keyboard() -> InlineKeyboardMarkup:
    """Inline клавиатура для подтверждения"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Скасувати", callback_data="confirm_no"),
            ],
        ]
    )


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для запроса номера телефона"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Надати номер телефону", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def back_to_menu_keyboard() -> ReplyKeyboardMarkup:
    """Простая клавиатура с кнопкой возврата в меню"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
    )

def utility_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Переповнений смітник")],
            [KeyboardButton(text="Наслідки негоди")],
            [KeyboardButton(text="Зачинене бомбосховище")],
            [KeyboardButton(text="Засмічення")],
            [KeyboardButton(text="Інший випадок")],
            [KeyboardButton(text=BTN_BACK)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
