from aiogram import Bot
from aiogram.types import Message

from app.telegram_bot.keyboards.main_kb import main_kb


async def get_start(message: Message, bot: Bot) -> None:
    await bot.send_message(
        message.from_user.id,
        "Вітаю👋\n\n⚠️ Бот розуміє тільки українську мову\n\n"
        "Оберіть де шукати кандидатів...",
        reply_markup=main_kb,
    )
