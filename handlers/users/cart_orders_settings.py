from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from loader import db, bot
from keyboards.inline.buttons import (cart_markup, branches_markup, order_markup, my_orders_markup,
                                      order_detail_markup_group)
from keyboards.reply.buttons import main_markup, settings_markup, phone_markup
from utils.extra_datas import calculate_discount_price
from states.states import UserState

router = Router()


@router.message(F.text == "Savatcha 🛒")
async def get_cart(message: types.Message, state: FSMContext):
    user = await db.get_user(telegram_id=message.from_user.id)
    cart_text = f"Savatcha 🛒:\n\n"
    cart_items = await db.select_user_cart_products(user_id=user.get("id"))
    total_price = 0
    products = []
    for item in cart_items:
        product = await db.get_product(id=item.get("product_id"))
        products.append(product)
        original_price, discount_percentage, discount_price = await calculate_discount_price(product)
        quantity = item.get('quantity')
        price = discount_price * quantity
        cart_text += f"<i>{product.get('name')} ({quantity}) - {price} so'm</i>\n"
        total_price += price
    cart_text += f"\n\n<b>💸Umumiy narx: {total_price} so'm</b>"
    if cart_items:
        await message.answer(text=cart_text, reply_markup=await cart_markup(products), parse_mode=ParseMode.HTML)
        await state.set_state(UserState.cart)
    else:
        await message.answer(
            "Savatingiz hozircha bo'm-bo'sh😔\n\nKeling uni birga to'ldiramiz😊"
            "\n\n<i>\"Xarid qilish 🛍\" tugmasini bosing</i>",
            parse_mode=ParseMode.HTML,
        )
        await state.set_state()


@router.callback_query(F.data == "cart")
async def cart(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(telegram_id=call.from_user.id)
    cart_text = f"Savatcha 🛒:\n\n"
    cart_items = await db.select_user_cart_products(user_id=user.get("id"))
    total_price = 0
    products = []
    for item in cart_items:
        product = await db.get_product(id=item.get("product_id"))
        products.append(product)
        original_price, discount_percentage, discount_price = await calculate_discount_price(product)
        quantity = item.get('quantity')
        price = discount_price * quantity
        cart_text += f"<i>{product.get('name')} ({quantity}) - {price} so'm</i>\n"
        total_price += price
    cart_text += f"\n\n<b>💸Umumiy narx: {total_price} so'm</b>"
    if cart_items:
        await call.message.edit_text(text=cart_text, reply_markup=await cart_markup(products), parse_mode=ParseMode.HTML)
        await state.set_state(UserState.cart)
    else:
        await call.message.edit_text(
            "Savatingiz hozircha bo'm-bo'sh😔\n\nKeling uni birga to'ldiramiz😊"
            "\n\n<i>\"Xarid qilish 🛍\" tugmasini bosing</i>",
            parse_mode=ParseMode.HTML,
        )
        await state.set_state()


@router.callback_query(UserState.cart)
async def cart_detail(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(telegram_id=call.from_user.id)
    if call.data == "back":
        await call.message.edit_text("Nimadan boshlaymiz?")
        await state.set_state()
    elif call.data.startswith("remove_"):
        product_id = int(call.data.split("_")[-1])
        await db.remove_product_from_cart(user_id=user.get("id"), product_id=product_id)
        cart_text = f"Savatcha 🛒:\n\n"
        cart_items = await db.select_user_cart_products(user_id=user.get("id"))
        total_price = 0
        products = []
        for item in cart_items:
            product = await db.get_product(id=item.get("product_id"))
            products.append(product)
            original_price, discount_percentage, discount_price = await calculate_discount_price(product)
            quantity = item.get('quantity')
            price = discount_price * quantity
            cart_text += f"<i>{product.get('name')} ({quantity}) - {price} so'm</i>\n"
            total_price += price
        cart_text += f"\n\n<b>💸Umumiy narx: {total_price} so'm</b>"
        if cart_items:
            await call.message.edit_text(text=cart_text, reply_markup=await cart_markup(products), parse_mode=ParseMode.HTML)
        else:
            await call.message.edit_text(
                "Savatingiz hozircha bo'm-bo'sh😔\n\nKeling uni birga to'ldiramiz😊"
                "\n\n<i>\"Xarid qilish 🛍\" tugmasini bosing</i>",
                parse_mode=ParseMode.HTML,
            )
            await state.set_state()
    elif call.data == "clear":
        await db.clear_cart(user_id=user.get("id"))
        await call.message.edit_text(
            "Savatingiz hozircha bo'm-bo'sh😔\n\nKeling uni birga to'ldiramiz😊"
            "\n\n<i>\"Xarid qilish 🛍\" tugmasini bosing</i>",
            parse_mode=ParseMode.HTML,
        )
        await state.set_state()
    elif call.data == "order":
        text, markup = await branches_markup(branches=await db.select_branches())
        await call.message.edit_text(
            f"🏢 Olib ketish uchun filialni tanlang:\n\n{text}",
            reply_markup=markup,
            disable_web_page_preview=True,
        )
        await state.set_state(UserState.branch)


@router.callback_query(UserState.branch)
async def get_branch(call: types.CallbackQuery, state: FSMContext):
    if call.data.isdigit():
        user = await db.get_user(telegram_id=call.from_user.id)
        user_id = user.get("id")
        user_cart = await db.select_user_cart_products(user_id=user_id)
        total_price = 0
        total_quantity = 0
        order_products = []
        for item in user_cart:
            product = await db.get_product(id=item.get("product_id"))
            quantity = item.get("quantity")
            original_price, discount_percentage, discount_price = await calculate_discount_price(product)
            total_price += discount_price * quantity
            total_quantity += quantity

            order_products.append({
                "id": product.get("id"),
                "quantity": quantity,
                "price": discount_price,
            })
        order = await db.add_order(
            user_id=user_id,
            total_price=total_price,
            quantity=total_quantity,
            branch_id=int(call.data)
        )
        for order_product in order_products:
            await db.add_order_product(
                order_id=order.get("id"),
                product_id=order_product.get("id"),
                quantity=order_product.get("quantity"),
                price=order_product.get("price"),
            )
        await db.clear_cart(user_id=user_id)
        order_id = order.get('id')
        text = ""
        cnt = 1
        for order_product in await db.select_order_products(order_id=order_id):
            product = await db.get_product(id=order_product.get("product_id"))
            text += f"{cnt}. {product.get('name')}\n"
            cnt += 1
        text += f"\n\n<b>💸Umumiy narx: {order.get('total_price')} so'm</b>"
        await call.message.edit_text(
            f"#{order_id} raqamli buyurtma:\n\n{text}",
            reply_markup=await order_markup(pay_link="https://payme.uz/", order_id=order.get("id")),
        )
        chats = await db.get_chats()
        for chat in chats:
            text, markup = await my_orders_markup([order])
            msg = await bot.send_message(
                chat_id=chat.get("chat_id"),
                text=text,
                reply_markup=await order_detail_markup_group(order_id=order_id)
            )
            await db.add_chat_order_message(
                chat_id=chat.get("id"),
                order_id=order.get("id"),
                message_id=msg.message_id,
            )
        await state.set_state(UserState.order)
    elif call.data == "back":
        user = await db.get_user(telegram_id=call.from_user.id)
        cart_text = f"Savatcha 🛒:\n\n"
        cart_items = await db.select_user_cart_products(user_id=user.get("id"))
        total_price = 0
        products = []
        for item in cart_items:
            product = await db.get_product(id=item.get("product_id"))
            products.append(product)
            original_price, discount_percentage, discount_price = await calculate_discount_price(product)
            quantity = item.get('quantity')
            price = discount_price * quantity
            cart_text += f"<i>{product.get('name')} ({quantity}) - {price} so'm</i>\n"
            total_price += price
        cart_text += f"\n\n<b>💸Umumiy narx: {total_price} so'm</b>"
        if cart_items:
            await call.message.edit_text(text=cart_text, reply_markup=await cart_markup(products),
                                         parse_mode=ParseMode.HTML)
            await state.set_state(UserState.cart)
        else:
            await call.message.edit_text(
                "Savatingiz hozircha bo'm-bo'sh😔\n\nKeling uni birga to'ldiramiz😊"
                "\n\n<i>\"Xarid qilish 🛍\" tugmasini bosing</i>",
                parse_mode=ParseMode.HTML,
            )
            await state.set_state()


@router.callback_query(UserState.order)
async def _order(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("cancel_"):
        await db.update_order_status(order_id=int(call.data.split("_")[-1]), status="canceled")
        chat_order_messages = await db.select_chat_order_messages(order_id=int(call.data.split("_")[-1]))
        for chat_msg in chat_order_messages:
            chat = await db.get_chat(id=chat_msg.get("chat_id"))
            order = await db.select_order(id=chat_msg.get("order_id"))
            text, markup = await my_orders_markup([order])
            await bot.edit_message_text(
                chat_id=chat.get("chat_id"),
                message_id=chat_msg.get("message_id"),
                text=text,
            )
        await call.message.edit_text("Buyurtma bekor qilindi!")
        await call.message.answer("Nimadan boshlaymiz?", reply_markup=main_markup)
        await state.set_state()


@router.message(F.text == "Buyurtmalarim 🗂")
async def my_orders(message: types.Message, state: FSMContext):
    user = await db.get_user(telegram_id=message.from_user.id)
    orders = await db.select_orders(user_id=user.get("id"))
    if orders:
        text, markup = await my_orders_markup(orders)
        await message.answer(text, reply_markup=markup)
        await state.set_state(UserState.my_orders)
    else:
        await message.answer(
            "Sizda hali buyurtmalar mavjud emas. "
            "Marhamat <b>\"Xarid qilish 🛍\"</b> tugmasi bosish orqali istagan mahsulotingizni"
            " xarid qiling va buyurtma bering😊",
            parse_mode=ParseMode.HTML,
        )


@router.callback_query(UserState.my_orders)
async def my_orders_paginate(call: types.CallbackQuery, state: FSMContext):
    if call.data == "back":
        await call.message.edit_text("Nimadan boshlaymiz?")
        await state.set_state()
    else:
        user = await db.get_user(telegram_id=call.from_user.id)
        orders = await db.select_orders(user_id=user.get("id"))
        action, index = call.data.split("_")
        text, markup = await my_orders_markup(orders, int(index))
        if text and markup:
            await call.message.edit_text(text, reply_markup=markup)


@router.message(F.text == "Sozlamalar ⚙️")
async def settings(message: types.Message, state: FSMContext):
    await message.answer("Tanlang", reply_markup=settings_markup)
    await state.set_state(UserState.settings)


@router.message(UserState.settings)
async def settings_actions(message: types.Message, state: FSMContext):
    if message.text == "Telefon raqamni o'zgartirish 📱":
        await message.answer("Yangi telefon raqamni +998901234567 formatida yozib yuboring yoki "
                             "\"Telefon raqamini ulashish 📱\" tugmasini bosing", reply_markup=phone_markup)
        await state.set_state(UserState.set_phone_number)
    elif message.text == "◀️️ Orqaga":
        await message.answer("Nimadan boshlaymiz?", reply_markup=main_markup)
        await state.set_state()
