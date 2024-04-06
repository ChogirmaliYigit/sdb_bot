import decimal

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from loader import db
from data.config import BACKEND_URL
from keyboards.inline.buttons import make_paginated_list_buttons, product_markup, cart_button
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
    if not call.data.isdigit():
        if call.data != "back":
            action, start, _id = call.data.split("_")
            await call.message.edit_reply_markup(
                reply_markup=await make_paginated_list_buttons(
                    data=await db.select_categories(),
                    start=int(start),
                )
            )
        else:
            await call.message.edit_text(text="Nimadan boshlaymiz?")
            await state.set_state()
    else:
        category = await db.get_category(id=int(call.data))
        if not category:
            await call.message.edit_text("Bunday kategoriya topilmadi.")
        else:
            sub_categories = await db.get_sub_categories(parent_id=category.get("id"))
            markup = await make_paginated_list_buttons(data=sub_categories, _id=category.get("id"))
            if category.get("image"):
                backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
                photo_url = f"{backend_url}/media/{category.get('image')}"
                await call.message.delete()
                await call.message.answer_photo(
                    photo=photo_url,
                    caption=f"{category.get('name')} kategoriyalarini tanlang:\n\n{category.get('description')}",
                    reply_markup=markup,
                )
            else:
                await call.message.edit_text(
                    text=f"{category.get('name')} kategoriyalarini tanlang:\n\n{category.get('description')}",
                    reply_markup=markup,
                )
            await state.set_state(UserState.sub_category)


@router.callback_query(UserState.sub_category)
async def get_sub_category(call: types.CallbackQuery, state: FSMContext):
    if not call.data.isdigit():
        if not call.data.startswith("back_"):
            action, start, _id = call.data.split("_")
            sub_categories = await db.get_sub_categories(parent_id=_id)
            await call.message.edit_reply_markup(
                reply_markup=await make_paginated_list_buttons(
                    data=sub_categories,
                    start=int(start),
                    _id=_id,
                )
            )
        else:
            await call.message.delete()
            await call.message.answer(
                text="Kategoriyani tanlang:",
                reply_markup=await make_paginated_list_buttons(
                    data=await db.select_categories(),
                )
            )
            await state.set_state(UserState.category)
    else:
        sub_category = await db.get_sub_category(id=int(call.data))
        if not sub_category:
            await call.message.edit_text("Bunday kategoriya topilmadi.")
        else:
            products = await db.select_category_products(category_id=sub_category.get("id"))
            markup = await make_paginated_list_buttons(
                data=products,
                _id=f"{sub_category.get('parent_id')}-{sub_category.get('id')}"
            )
            if sub_category.get("image"):
                backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
                photo_url = f"{backend_url}/media/{sub_category.get('image')}"
                await call.message.delete()
                await call.message.answer_photo(
                    photo=photo_url,
                    caption=f"{sub_category.get('name')} mahsulotlarini tanlang:\n\n{sub_category.get('description')}",
                    reply_markup=markup,
                )
            else:
                category = await db.get_category(id=sub_category.get("parent_id"))
                if category.get("image"):
                    await call.message.delete()
                    await call.message.answer(
                        f"{sub_category.get('name')} mahsulotlarini tanlang:\n\n{sub_category.get('description')}",
                        reply_markup=markup
                    )
                else:
                    await call.message.edit_text(
                        f"{sub_category.get('name')} mahsulotlarini tanlang:\n\n{sub_category.get('description')}",
                        reply_markup=markup
                    )
            await state.set_state(UserState.product)


@router.callback_query(UserState.product)
async def get_product(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith("back_"):
        action, _id = call.data.split("_")
        category_id = int(_id.split("-")[0])
        sub_category_id = int(_id.split("-")[-1])
        sub_categories = await db.get_sub_categories(parent_id=category_id)
        category = await db.get_category(id=category_id)
        sub_category = await db.get_sub_category(id=sub_category_id)
        markup = await make_paginated_list_buttons(
            data=sub_categories,
            _id=_id,
        )
        if category.get("image"):
            backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
            photo_url = f"{backend_url}/media/{category.get('image')}"
            await call.message.delete()
            await call.message.answer_photo(
                photo=photo_url,
                caption=f"{category.get('name')} kategoriyalarini tanlang:\n\n{category.get('description')}",
                reply_markup=markup,
            )
        else:
            if sub_category.get("image"):
                backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
                photo_url = f"{backend_url}/media/{category.get('image')}"
                await call.message.delete()
                await call.message.answer_photo(
                    photo=photo_url,
                    caption=f"{category.get('name')} kategoriyalarini tanlang:\n\n{category.get('description')}",
                    reply_markup=markup,
                )
            else:
                await call.message.edit_text(
                    text=f"{category.get('name')} kategoriyalarini tanlang:\n\n{category.get('description')}",
                    reply_markup=markup,
                )
        await state.set_state(UserState.sub_category)
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
        sub_category = await db.get_sub_category(id=int(_id))
        products = await db.select_category_products(category_id=sub_category.get("id"))
        markup = await make_paginated_list_buttons(
            data=products,
            _id=f"{sub_category.get('parent_id')}-{sub_category.get('id')}"
        )
        if sub_category.get("image"):
            backend_url = BACKEND_URL[:-1] if BACKEND_URL.endswith("/") else BACKEND_URL
            photo_url = f"{backend_url}/media/{sub_category.get('image')}"
            await call.message.delete()
            await call.message.answer_photo(
                photo=photo_url,
                caption=f"{sub_category.get('name')} mahsulotlarini tanlang:\n\n{sub_category.get('description')}",
                reply_markup=markup,
            )
        else:
            category = await db.get_category(id=sub_category.get("parent_id"))
            if category.get("image"):
                await call.message.delete()
                await call.message.answer(
                    f"{sub_category.get('name')} mahsulotlarini tanlang:\n\n{sub_category.get('description')}",
                    reply_markup=markup
                )
            else:
                await call.message.edit_text(
                    f"{sub_category.get('name')} mahsulotlarini tanlang:\n\n{sub_category.get('description')}",
                    reply_markup=markup
                )
        await state.set_state(UserState.product)
    elif call.data.startswith("plus_") or call.data.startswith("minus_"):
        action, product_count, product_id = call.data.split("_")
        product_count = decimal.Decimal(product_count)
        if int(product_count) > 0:
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

            await call.message.edit_caption(
                caption=description,
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
