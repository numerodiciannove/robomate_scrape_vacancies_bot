from aiogram import Bot
from aiogram.types import Message

from app.telegram_bot.keyboards.main_kb import main_kb


async def get_start(message: Message, bot: Bot) -> None:
    await bot.send_message(
        message.from_user.id,
        f"Вітаю👋!\n\nОберіть де шукати кандидатів...",
        reply_markup=main_kb
    )
