from aiogram.fsm.state import StatesGroup, State


class Phone(StatesGroup):
    phone = State()
