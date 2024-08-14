import asyncio
from concurrent.futures import ThreadPoolExecutor

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.parsers.main import get_rabota_ua_top_5_cvs
from app.telegram_bot.keyboards.main_kb import main_kb
from app.telegram_bot.keyboards.rabota_ua_experience_generator_kb import experience_kb
from app.telegram_bot.state.rabota_ua_state import RabotaUaState


executor = ThreadPoolExecutor()


async def start_rabota_ua_parser(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    await bot.send_message(message.from_user.id, "Давай почнемо💫")
    await bot.send_message(
        message.from_user.id,
        (
            "✍️ Напишіть наички за якими ви шукаєте кандидатів\n\n"
            "Наприклад:\n\n"
            "Кухар сушист\n\n"
            "🔁 або\n\n"
            "Python django"
        ),
        reply_markup=None,
    )
    await state.set_state(RabotaUaState.position)


async def rabota_register_cvs_position(
    message: Message, state: FSMContext, bot: Bot
) -> None:
    await state.update_data(position=message.text)
    await bot.send_message(
        message.from_user.id,
        (
            "✍️ Напишіть місто в якому шукати кандидатів\n\n"
            "Наприклад:\n\n"
            "Київ\n\n"
            "🔁 або\n\n"
            "Одеса"
        ),
        reply_markup=None,
    )
    await state.set_state(RabotaUaState.city)


async def rabota_register_cvs_city(
    message: Message, state: FSMContext, bot: Bot
) -> None:
    await state.update_data(city=message.text)
    await bot.send_message(
        message.from_user.id,
        "Виберіть досвід роботи кандидата:",
        reply_markup=await experience_kb(),
    )
    await state.set_state(RabotaUaState.experience)


async def rabota_register_cvs_experience(
    callback_query: CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    await state.update_data(experience=callback_query.data)
    await callback_query.answer()

    user_data = await state.get_data()

    position = user_data.get("position")
    city = user_data.get("city")
    experience = user_data.get("experience")

    if not position or not city or not experience:
        await bot.send_message(
            callback_query.from_user.id,
            "Будь ласка, переконайтесь, що ви ввели всі необхідні дані (посада, місто, досвід роботи).",
        )
        return

    await bot.send_message(
        callback_query.from_user.id,
        (
            f"Ви вибрали:\n\n"
            f"🔹 Посада: {position}\n"
            f"🔹 Місто: {city}\n"
            f"🔹 Досвід роботи: {experience}\n\n"
            "Шукаю топ 5 кандидатів..."
        ),
    )

    loop = asyncio.get_running_loop()
    top_5_cv = await loop.run_in_executor(
        None,
        get_rabota_ua_top_5_cvs,
        position,  # Передача именованных аргументов
        city,
        experience,
    )

    if not top_5_cv:
        await bot.send_message(
            callback_query.from_user.id,
            "Не вдалося знайти кандидатів за заданими параметрами. Спробуйте інші параметри.",
            reply_markup=main_kb,
        )
    else:
        for cv in top_5_cv:
            message_text = (
                f"👤 Ім'я: {cv.name}\n"
                f"📅 Вік: {cv.age}\n"
                f"📍 Місто: {cv.location or 'Unknown'}\n"
                f"🔗 Ссилка на резюме: {cv.url}"
            )
            await bot.send_message(callback_query.from_user.id, message_text)

    await state.clear()
