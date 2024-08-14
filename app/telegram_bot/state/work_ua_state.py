from aiogram.fsm.state import StatesGroup, State


class WorkUaState(StatesGroup):
    position = State()
    city = State()
    experience = State()
