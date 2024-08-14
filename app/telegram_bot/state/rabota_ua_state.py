from aiogram.fsm.state import StatesGroup, State


class RabotaUaState(StatesGroup):
    position = State()
    city = State()
    experience = State()
