from aiogram import Router
from aiogram.enums.chat_type import ChatType
from filters import ChatTypeFilter


def setup_routers() -> Router:
    from .users import admin, start, order, cart_orders_settings
    from .errors import error_handler
    from .groups import start as group_start

    router = Router()

    start.router.message.filter(ChatTypeFilter(chat_type=ChatType.PRIVATE))
    group_start.router.message.filter(ChatTypeFilter(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP]))

    router.include_routers(admin.router, start.router, order.router, cart_orders_settings.router,
                           error_handler.router, group_start.router)

    return router
