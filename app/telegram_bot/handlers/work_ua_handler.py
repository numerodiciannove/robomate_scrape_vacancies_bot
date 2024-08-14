from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.parsers.main import get_work_ua_top_5_cvs
from app.telegram_bot.keyboards.main_kb import main_kb
from app.telegram_bot.keyboards.work_ua_experience_generator_kb import experience_kb
from app.telegram_bot.state.work_ua_state import WorkUaState


async def start_work_ua_parser(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    await bot.send_message(message.from_user.id, "Давай почнемо💫")
    await bot.send_message(
        message.from_user.id,
        (
            "✍️ Напишіть на яку посаду ви шукаєте кандидатів\n\n"
            "Наприклад:\n\n"
            "Кухар\n\n"
            "🔁 або\n\n"
            "Python developer"
        ),
        reply_markup=None,
    )
    await state.set_state(WorkUaState.position)


async def register_cvs_position(message: Message, state: FSMContext, bot: Bot) -> None:
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
    await state.set_state(WorkUaState.city)


async def register_cvs_city(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(city=message.text)
    await bot.send_message(
        message.from_user.id,
        "Виберіть досвід роботи кандидата:",
        reply_markup=await experience_kb(),
    )
    await state.set_state(WorkUaState.experience)


async def register_cvs_experience(
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

    top_5_cv = await get_work_ua_top_5_cvs(
        position=position,
        location=city,
        experience=experience
    )

    if not top_5_cv:
        await bot.send_message(
            callback_query.from_user.id,
            "Не вдалося знайти кандидатів за заданими параметрами. Спробуйте інші параметри.",
            reply_markup=main_kb,
        )
    else:
        for cv in top_5_cv:
            await bot.send_message(
                callback_query.from_user.id,
                (
                    f"👤 Ім'я: {cv.name}\n"
                    f"📅 Вік: {cv.age}\n"
                    f"📍 Місто: {cv.location}\n"
                    f"💼 Навички: {', '.join(cv.skills)}\n"
                    f"🔗 Ссилка на резюме: {cv.url}"
                ),
            )
