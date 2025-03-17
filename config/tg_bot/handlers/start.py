import re

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery

from data.account.models import CustomUser
from dispatcher import dp
from tg_bot.buttons.reply import *
from tg_bot.state.main import Phone


@dp.message(lambda msg: msg.text == "/start")
async def command_start_handler(message: Message, state: FSMContext) -> None:

    await state.set_state(Phone.phone)
    await message.answer(
        text="Assalomu alaykum, botdan foydalanish uchun avval telefon raqamingizni bosing !",
        reply_markup=phone_number_btn()
    )

def format_phone_number(phone_number: str) -> str:

    phone_number = ''.join(c for c in phone_number if c.isdigit())

    # Prepend +998 if missing
    if phone_number.startswith('998'):
        phone_number = '+' + phone_number
    elif not phone_number.startswith('+998'):
        phone_number = '+998' + phone_number

    # Check final phone number length
    if len(phone_number) == 13:
        return phone_number
    else:
        raise ValueError("Invalid phone number length")

@dp.message(Phone.phone)
async def callback_start_handler(message: Message, state: FSMContext) -> None:
    if message.contact:
        phone_number = message.contact.phone_number
        phone_number = format_phone_number(phone_number)

        user = CustomUser.objects.filter(phone=phone_number , role__in = ["DIRECTOR", "MULTIPLE_FILIAL_MANAGER"]).first()
        if user:

            user.chat_id = message.from_user.id
            user.save()

            await message.answer(
                f"{user.full_name} botga xush kelibsiz, "
                f"ushbu bot orqali siz har kunlik xisobotlar bilan tanishib borishingiz mumkin!"
            )
        else:
            await message.answer(
                f"{message.from_user.full_name} kechirasiz, sizda botdan foydalanish buyicha kerakli ruxsat mavjud emas ! "
            )


    elif message.text and re.match(r"^\+\d{9,13}$", message.text):
        phone_number = message.text
        phone_number = format_phone_number(phone_number)
        user = CustomUser.objects.filter(phone=phone_number , role__in = ["DIRECTOR", "MULTIPLE_FILIAL_MANAGER"]).first()
        if user:
            await message.answer(
                f"{user.full_name} botga xush kelibsiz, "
                f"ushbu bot orqali siz har kunlik xisobotlar bilan tanishib borishingiz mumkin!"
            )

            user.chat_id = message.from_user.id
            user.save()

        else:
            await message.answer(
                f"{message.from_user.full_name} kechirasiz, sizda botdan foydalanish buyicha kerakli ruxsat mavjud emas ! "
            )







