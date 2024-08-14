from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from app.parsers.site_configs.work_ua import WORK_UA_EXPERIENCE_CATEGORIES
from app.telegram_bot.utils.inline_keyboard_builder import InlineKeyboardBuilder


async def experience_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for experience in WORK_UA_EXPERIENCE_CATEGORIES.keys():
        kb.button(text=f"{experience}", callback_data=f"{experience}")

        kb.adjust(1)

    return kb.as_markup()
