from typing import Tuple, Union
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import db

inline_keyboard = [[
    InlineKeyboardButton(text="✅ Yes", callback_data='yes'),
    InlineKeyboardButton(text="❌ No", callback_data='no')
]]
are_you_sure_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

back_button = InlineKeyboardButton(text="◀️ Orqaga", callback_data="back")


async def make_paginated_list_buttons(data: list, start: int = 0, _id: str = None) -> InlineKeyboardMarkup:
    keyboard = []
    for item in data[start:int(start) + 10:2]:
        row = [
            InlineKeyboardButton(text=item.get("name"), callback_data=str(item.get("id")))
        ]
        try:
            item = data[int(data.index(item)) + 1]
            row.append(InlineKeyboardButton(text=item.get("name"), callback_data=str(item.get("id"))))
        except (IndexError, AttributeError):
            pass
        keyboard.append(row)

    pagination_keyboard = []
    if data[start + 10:]:
        pagination_keyboard.append(InlineKeyboardButton(text="Keyingi➡️", callback_data=f"next_{start + 10}_{_id}"))
    if start > 0:
        pagination_keyboard.append(InlineKeyboardButton(text="⬅️Oldingi", callback_data=f"prev_{start - 10}_{_id}"))

    keyboard.append(pagination_keyboard)
    keyboard.append([
        InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"back_{_id}") if _id else back_button
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def product_markup(product_id: int, count: int = 1, _id: str = None) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="➖", callback_data=f"minus_{count - 1}_{product_id}"),
            InlineKeyboardButton(text=str(count), callback_data="count"),
            InlineKeyboardButton(text="➕", callback_data=f"plus_{count + 1}_{product_id}"),
        ],
        [
            InlineKeyboardButton(text="Savatchaga qo'shish 🛒", callback_data=f"add_to_cart_{count}_{product_id}"),
        ],
        [
            InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"back_{_id}") if _id else back_button
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def cart_markup(products: list) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="🤝 Rasmiylashtirish", callback_data="order"),
        ],
        [
            back_button,
            InlineKeyboardButton(text="Savatni tozalash 🗑", callback_data="clear"),
        ],
    ]
    for product in products:
        keyboard.append([
            InlineKeyboardButton(text=f"❌{product.get('name')}", callback_data=f"remove_{product.get('id')}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


cart_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Savatcha 🛒", callback_data="cart"),
        ],
    ],
)


async def branches_markup(branches) -> Tuple[str, InlineKeyboardMarkup]:
    keyboard = []
    count = 1
    text = str()
    for item in branches[::2]:
        row = [
            InlineKeyboardButton(text=str(count), callback_data=str(item.get("id")))
        ]
        text += (f"{count}. <a href='https://www.google.com/maps/"
                 f"@{item.get('latitude')},{item.get('longitude')},18.5z?entry=ttu'>{item.get('name')} - {item.get('description')}</a>\n")
        try:
            item = branches[int(branches.index(item)) + 1]
            row.append(InlineKeyboardButton(text=str(count + 1), callback_data=str(item.get("id"))))
            text += (f"{count + 1}. <a href='https://www.google.com/maps/"
                     f"@{item.get('latitude')},{item.get('longitude')},18.5z?entry=ttu'>{item.get('name')} - {item.get('description')}</a>\n")
        except (IndexError, AttributeError):
            pass
        keyboard.append(row)
        count += 2

    keyboard.append([back_button])
    return text, InlineKeyboardMarkup(inline_keyboard=keyboard)


async def order_markup(pay_link: str, order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="To'lov qilish", url=pay_link),
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_{order_id}"),
            ],
        ],
    )


async def my_orders_markup(orders, index: int = 0) -> Tuple[str, Union[InlineKeyboardMarkup, None]]:
    try:
        order = orders[index]
    except IndexError:
        return "", None

    user = await db.get_user(id=order.get("user_id"))
    order_statuses = {
        "in_processing": "Jarayonda",
        "confirmed": "Tasdiqlangan",
        "success": "Muvaffaqiyatli",
        "canceled": "Bekor qilingan",
        "payment_canceled": "To'lov bekor qilingan",
        "refunded": "Qaytarilgan",
    }
    payment_status = "To'langan✅" if order.get("is_paid") else "To'lanmagan❌"
    branch = await db.get_branch(id=order.get("branch_id"))
    order_products = await db.select_order_products(order_id=order.get("id"))
    product_names = []
    for order_product in order_products:
        product = await db.get_product(id=order_product.get("product_id"))
        product_names.append(product.get("name"))

    text = (f"<b>№{order.get('id')} raqamli buyurtma:</b>\n\n"
            f"📱Telefon raqam: {user.get('phone_number')}\n"
            f"📦Holati: <u>{order_statuses.get(order.get('status'))}</u>\n"
            f"💸To'lov holati: {payment_status}\n"
            f"🏢Filial: {branch.get('name')}\n"
            f"📋Mahsulotlar: <b>{', '.join(product_names)}</b>\n\n"
            f"<b>💸Umumiy narx: {order.get('total_price')} so'm</b>")

    pagination_keyboard = []
    if orders[:index]:
        pagination_keyboard.append(InlineKeyboardButton(text="⬅️", callback_data=f"previous_{index - 1}"))
    if orders[index+1:]:
        pagination_keyboard.append(InlineKeyboardButton(text="➡️", callback_data=f"next_{index + 1}"))

    return text, InlineKeyboardMarkup(inline_keyboard=[pagination_keyboard, [back_button]])


async def order_detail_markup_group(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Tasdiqlash✅", callback_data=f"confirm_{order_id}"),
                InlineKeyboardButton(text="Bekor qilish❌", callback_data=f"cancel_{order_id}"),
            ],
        ],
    )
