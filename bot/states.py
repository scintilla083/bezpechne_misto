from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    waiting_for_city = State()
    waiting_for_phone = State()


class MainMenuState(StatesGroup):
    main = State()


class PoliceState(StatesGroup):
    choosing_category = State()
    collecting = State()
    confirming = State()


class UtilityState(StatesGroup):
    collecting = State()
    confirming = State()


class MayorState(StatesGroup):
    collecting = State()
    confirming = State()


class FeedbackState(StatesGroup):
    collecting = State()


class ChangeCityState(StatesGroup):
    waiting_for_city = State()
