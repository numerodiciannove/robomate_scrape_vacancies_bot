from dotenv import load_dotenv
import asyncio
import logging
import os


from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

from app.telegram_bot.handlers.rabota_ua_handler import (
    start_rabota_ua_parser,
    rabota_register_cvs_position,
    rabota_register_cvs_city,
    rabota_register_cvs_experience,
)
from app.telegram_bot.handlers.work_ua_handler import (
    start_work_ua_parser,
    work_register_cvs_position,
    work_register_cvs_city,
    work_register_cvs_experience,
)

from app.telegram_bot.state.rabota_ua_state import RabotaUaState
from handlers.start import get_start
from utils.commands import set_commands
from state.work_ua_state import WorkUaState


load_dotenv()

ADMIN_ID = os.environ["ADMIN_ID"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()


# Send a message to admin when bot started
async def start_bot(bot: Bot) -> None:
    await bot.send_message(ADMIN_ID, text="Bot started!")


# Start message
dp.startup.register(start_bot)
dp.message.register(get_start, Command(commands="start"))

# Get work.ua top 5 CV
dp.message.register(start_work_ua_parser, F.text == "🤓 work.ua")
dp.message.register(work_register_cvs_position, WorkUaState.position)
dp.message.register(work_register_cvs_city, WorkUaState.city)
dp.callback_query.register(
    work_register_cvs_experience,
    WorkUaState.experience
)

# Get rabota.ua top 5 CV
dp.message.register(start_rabota_ua_parser, F.text == "🤓 rabota.ua")
dp.message.register(rabota_register_cvs_position, RabotaUaState.position)
dp.message.register(rabota_register_cvs_city, RabotaUaState.city)
dp.callback_query.register(
    rabota_register_cvs_experience,
    RabotaUaState.experience
)


async def main() -> None:
    # Menu commands
    await set_commands(bot)

    logging.basicConfig(level=logging.INFO)

    try:
        await dp.start_polling(bot, skip_update=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
