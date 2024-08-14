from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤓 work.ua")],
        [KeyboardButton(text="🤓 rabota.ua")]
    ],
    resize_keyboard=True
)
