from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup

from app.parsers.site_configs.rabota_ua import RABOTA_UA_EXPERIENCE_DICT
from app.telegram_bot.utils.inline_keyboard_builder import (
    InlineKeyboardBuilder
)


async def experience_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for experience in RABOTA_UA_EXPERIENCE_DICT.keys():
        kb.button(text=f"{experience}", callback_data=f"{experience}")

        kb.adjust(1)

    return kb.as_markup()
