from aiogram.filters.state import StatesGroup, State


class UserState(StatesGroup):
    set_phone_number = State()
    category = State()
    sub_category = State()
    product = State()
    product_detail = State()
    cart = State()
    settings = State()
    branch = State()
    order = State()
    my_orders = State()


class AdminState(StatesGroup):
    are_you_sure = State()
    ask_ad_content = State()
