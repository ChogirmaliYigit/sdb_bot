from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from loader import db, bot
from keyboards.inline.buttons import my_orders_markup

router = Router()


@router.message(CommandStart())
async def group_start(message: types.Message):
    try:
        await message.reply("Shu yerdaman!")
        chat_id = message.chat.id
        await db.add_chat(chat_id=chat_id)
        print(f"New chat added: {chat_id}")
    except TelegramBadRequest as error:
        print(error)


@router.callback_query()
async def order_detail(call: types.CallbackQuery):
    if call.data.startswith("confirm_") or call.data.startswith("cancel_"):
        action, order_id = call.data.split("_")
        order_id = int(order_id)
        status = "confirmed" if action == "confirm" else "canceled"
        await db.update_order_status(order_id=order_id, status=status)
        order = await db.select_order(id=order_id)
        text, markup = await my_orders_markup([order])
        await call.message.edit_text(text=text)
        user = await db.get_user(id=int(order.get("user_id")))
        await bot.send_message(
            chat_id=user.get("telegram_id"),
            text=f"#{order_id} raqamli buyurtmangiz {'bekor qilindi😔' if status == 'canceled' else 'qabul qilindi🥳'}"
        )
