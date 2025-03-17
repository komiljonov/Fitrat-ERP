from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from tg_bot.buttons.text import *


def phone_number_btn():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = "Raqamni yuborish 📞",
                                                         request_contact=True) ]] ,
                               resize_keyboard=True)
