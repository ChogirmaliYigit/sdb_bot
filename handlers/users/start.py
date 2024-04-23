import re
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.enums.content_type import ContentType
from aiogram.client.session.middlewares.request_logging import logger
from aiogram.fsm.context import FSMContext
from asyncpg.exceptions import UniqueViolationError
from loader import db, bot
from data.config import ADMINS
from utils.extra_datas import make_title
from keyboards.reply.buttons import phone_markup, main_markup
from states.states import UserState

router = Router()


@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    user = None
    try:
        user = await db.add_user(telegram_id=telegram_id, full_name=full_name)
    except Exception as error:
        logger.info(error)
    if user:
        count = await db.count_users()
        msg = f"[{make_title(user['full_name'])}](tg://user?id={user['telegram_id']}) bazaga qo'shildi\.\nBazada {count} ta foydalanuvchi bor\."
    else:
        msg = f"[{make_title(full_name)}](tg://user?id={telegram_id}) bazaga oldin qo'shilgan"
    for admin in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=msg,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        except Exception as error:
            logger.info(f"Data did not send to admin: {admin}. Error: {error}")
    await message.answer(
        f"Assalomu alaykum {make_title(full_name)}\!",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    user = await db.get_user(telegram_id=telegram_id)
    if not user.get("phone_number"):
        await message.answer("Telefon raqamingizni yuboring.", reply_markup=phone_markup)
        await state.set_state(UserState.set_phone_number)
    else:
        await message.answer("Nimadan boshlaymiz?", reply_markup=main_markup)
        await state.clear()


@router.message(UserState.set_phone_number)
async def start_user(message: types.Message, state: FSMContext):
    phone_number = ""
    if message.content_type == ContentType.CONTACT:
        phone_number = message.contact.phone_number
        if not phone_number.startswith("+"):
            phone_number = f"+{phone_number}"
    elif message.content_type == ContentType.TEXT:
        if message.text == "◀️️ Orqaga":
            user = await db.get_user(telegram_id=message.from_user.id)
            if not user.get("phone_number"):
                await message.answer("Telefon raqamingizni yuboring.", reply_markup=phone_markup)
            else:
                await message.answer("Nimadan boshlaymiz?", reply_markup=main_markup)
                await state.clear()
            return
        else:
            phone_number = message.text

    if not re.match(
            "^\+?998?\s?-?([0-9]{2})\s?-?(\d{3})\s?-?(\d{2})\s?-?(\d{2})$",
            phone_number,
    ):
        await message.answer("Noto'g'ri format!\nRaqamni quyidagicha formatlarda kiritishingiz mumkin!"
                             "\n\n+998XXXXXXXXX, +998-XX-XXX-XX-XX, +998 XX XXX XX XX")
        phone_number = None

    if phone_number:
        try:
            await db.update_user_phone_number(phone_number=phone_number, telegram_id=message.from_user.id)
            await message.answer("Telefon raqam saqlandi!✅", reply_markup=types.ReplyKeyboardRemove())
            await message.answer("Nimadan boshlaymiz?", reply_markup=main_markup)
            await state.clear()
        except UniqueViolationError as err:
            logger.error(err)
            await message.answer("Ushbu telefon raqam oldin ro'yxatga olingan, boshqa raqamni sinab ko'ring.")
