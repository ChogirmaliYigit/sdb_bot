from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


back_button = KeyboardButton(text="◀️️ Orqaga")

phone_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Telefon raqamini ulashish 📱",
                request_contact=True,
            ),
        ],
        [back_button],
    ],
    resize_keyboard=True,
)


main_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Xarid qilish 🛍"),
        ],
        [
            KeyboardButton(text="Savatcha 🛒"),
            KeyboardButton(text="Buyurtmalarim 🗂"),
        ],
        [
            KeyboardButton(text="Sozlamalar ⚙️"),
            KeyboardButton(text="Filiallar 🏢"),
        ],
    ],
    resize_keyboard=True,
)


settings_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Telefon raqamni o'zgartirish 📱"),
        ],
        [back_button],
    ],
    resize_keyboard=True,
)
