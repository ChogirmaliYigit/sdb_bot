import decimal

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from loader import db
from data.config import BACKEND_URL
from keyboards.inline.buttons import make_paginated_list_buttons, product_markup, cart_button
from keyboards.reply.buttons import main_markup
from states.states import UserState
from utils.extra_datas import calculate_discount_price

router = Router()


@router.message(F.text == "Xarid qilish 🛍")
async def start_order_process(message: types.Message, state: FSMContext):
    await message.answer(
        "Kategoriyani tanlang:",
        reply_markup=await make_paginated_list_buttons(
            data=await db.select_categories(),
        )
    )
    await state.set_state(UserState.category)


@router.callback_query(UserState.category)
async def get_category(call: types.CallbackQuery, state: FSMContext):
    if call.data.isdigit():
        category = await db.get_category(id=int(call.data))
        products = await db.select_category_products(category_id=category.get("id"))
        markup = await make_paginated_list_buttons(
            data=products,
            _id=f"{category.get('id')}"
        )
        text = f"{category.get('name')} mahsulotlarini tanlang:\n\n{category.get('description')}"
        if category.get("image"):
            backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
            photo_url = f"{backend_url}/media/{category.get('image')}"
            await call.message.delete()
            await call.message.answer_photo(
                photo=photo_url,
                caption=text,
                reply_markup=markup,
            )
        else:
            await call.message.edit_text(text=text, reply_markup=markup)
        await state.set_state(UserState.product)
    else:
        if call.data == "back":
            await call.message.delete()
            await call.message.answer("Nimadan boshlaymiz?", reply_markup=main_markup)
            await state.set_state()
        else:
            action, start, _id = call.data.split("_")
            await call.message.edit_reply_markup(
                reply_markup=await make_paginated_list_buttons(
                    data=await db.select_categories(),
                    start=int(start),
                )
            )


@router.callback_query(UserState.product)
async def get_product(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("back_"):
        await call.message.delete()
        await call.message.answer(
            "Kategoriyani tanlang:",
            reply_markup=await make_paginated_list_buttons(
                data=await db.select_categories(),
            )
        )
        await state.set_state(UserState.category)
    else:
        await call.message.delete()
        product = await db.get_product(id=int(call.data))

        description = f"<b>{product.get('name')}</b>\n\n<i>{product.get('description')}</i>\n\n"

        product_count = decimal.Decimal(1)
        original_price, discount_percentage, discount_price = await calculate_discount_price(product)

        if discount_percentage == 0:
            description += f"<b>Narxi: {product_count} x {original_price} = {product_count * original_price} so'm</b>"
        else:
            description += (f"<b>Narxi: <del>{product_count} x {original_price} = {product_count * original_price}</del>"
                            f" {product_count} x {discount_price} = {product_count * discount_price} so'm "
                            f"({discount_percentage}% chegirma bilan)</b>")

        markup = await product_markup(product_id=product.get("id"), _id=product.get("category_id"))
        if product.get("image"):
            backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
            photo_url = f"{backend_url}/media/{product.get('image')}"
            await call.message.answer_photo(
                photo=photo_url,
                caption=description,
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
            )
        else:
            await call.message.answer(description, parse_mode=ParseMode.HTML, reply_markup=markup)
        await state.set_state(UserState.product_detail)


@router.callback_query(UserState.product_detail)
async def product_detail(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=0)
    user = await db.get_user(telegram_id=call.from_user.id)
    if call.data.startswith("back_"):
        action, _id = call.data.split("_")
        category = await db.get_category(id=int(_id))
        products = await db.select_category_products(category_id=category.get("id"))
        markup = await make_paginated_list_buttons(
            data=products,
            _id=f"{category.get('id')}"
        )
        text = f"{category.get('name')} mahsulotlarini tanlang:\n\n{category.get('description')}"
        if category.get("image"):
            backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
            photo_url = f"{backend_url}/media/{category.get('image')}"
            await call.message.delete()
            await call.message.answer_photo(
                photo=photo_url,
                caption=text,
                reply_markup=markup,
            )
        else:
            await call.message.edit_text(text=text, reply_markup=markup)
        await state.set_state(UserState.product)
    elif call.data.startswith("plus_") or call.data.startswith("minus_"):
        action, product_count, product_id = call.data.split("_")
        product_count = decimal.Decimal(product_count)
        if product_count > decimal.Decimal(0):
            product = await db.get_product(id=int(product_id))
            description = f"<b>{product.get('name')}</b>\n\n<i>{product.get('description')}</i>\n\n"

            original_price, discount_percentage, discount_price = await calculate_discount_price(product)

            if discount_percentage == 0:
                description += f"<b>Narxi: {product_count} x {original_price} = {product_count * original_price} so'm</b>"
            else:
                description += (
                    f"<b>Narxi: <del>{product_count} x {original_price} = {product_count * original_price}</del>"
                    f" {product_count} x {discount_price} = {product_count * discount_price} so'm "
                    f"({discount_percentage}% chegirma bilan)</b>")

            if product.get("image"):
                await call.message.edit_caption(
                    caption=description,
                    reply_markup=await product_markup(product_id=product_id, count=int(product_count))
                )
            else:
                await call.message.edit_text(
                    text=description,
                    reply_markup=await product_markup(product_id=product_id, count=int(product_count))
                )
    elif call.data.startswith("add_to_cart_"):
        product_id = int(call.data.split("_")[-1])
        product = await db.get_product(id=product_id)
        await db.add_to_cart(
            user_id=user.get("id"),
            product_id=product_id,
            quantity=int(call.data.split("_")[-2]),
        )
        text = "Mahsulot savatchaga qo'shildi✅\n\nDavom etamizmi?"
        if product.get("image"):
            await call.message.delete()
            await call.message.answer(text, reply_markup=cart_button)
        else:
            await call.message.edit_text(text, reply_markup=cart_button)
        await state.set_state()
