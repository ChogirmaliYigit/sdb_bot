import decimal
from typing import Union

import asyncpg

from data import config


class Database:
    """
    A database class
    """
    def __init__(self):
        """
        An initializer for the Database class
        """
        self.pool: Union[asyncpg.pool.Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: asyncpg.Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, telegram_id: int, full_name: str = ""):
        sql = "INSERT INTO telegram_users (full_name, telegram_id) VALUES ($1, $2) RETURNING *"
        return await self.execute(sql, full_name, telegram_id, fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM telegram_users"
        return await self.execute(sql, fetch=True)

    async def get_user(self, **kwargs):
        sql = "SELECT * FROM telegram_users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def get_product(self, **kwargs):
        sql = "SELECT * FROM products WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def get_category(self, **kwargs):
        sql = "SELECT * FROM categories WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_categories(self):
        sql = "SELECT * FROM categories"
        return await self.execute(sql, fetch=True)

    async def select_category_products(self, category_id: int):
        sql = "SELECT * FROM products WHERE category_id = $1 AND quantity > 0"
        return await self.execute(sql, category_id, fetch=True)

    async def add_to_cart(self, user_id: int, product_id: int, quantity: int):
        exists = await self.execute(
            "SELECT 1 FROM carts WHERE user_id = $1 AND product_id = $2;",
            user_id, product_id,
            fetchrow=True,
        )
        if exists:
            sql = "UPDATE carts SET quantity = quantity + $3 WHERE user_id = $1 AND product_id = $2;"
        else:
            sql = "INSERT INTO carts (user_id, product_id, quantity) VALUES ($1, $2, $3);"
        return await self.execute(sql, user_id, product_id, quantity, fetchrow=True)

    async def select_user_cart_products(self, user_id: int):
        sql = "SELECT * FROM carts WHERE user_id = $1"
        return await self.execute(sql, user_id, fetch=True)

    async def remove_product_from_cart(self, user_id: int, product_id: int):
        sql = "DELETE FROM carts WHERE user_id = $1 AND product_id = $2"
        return await self.execute(sql, user_id, product_id, fetchrow=True)

    async def clear_cart(self, user_id: int):
        sql = "DELETE FROM carts WHERE user_id = $1"
        return await self.execute(sql, user_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM telegram_users"
        return await self.execute(sql, fetchval=True)

    async def update_user_phone_number(self, phone_number, telegram_id):
        sql = "UPDATE telegram_users SET phone_number=$1 WHERE telegram_id=$2"
        return await self.execute(sql, phone_number, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM telegram_users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE telegram_users", execute=True)

    async def add_order(
            self,
            user_id: int,
            total_price: decimal.Decimal,
            quantity: int,
            is_paid: bool = False,
            status: str = "in_processing",
            branch_id: int = None,
    ):
        sql = ("INSERT INTO orders (user_id, total_price, quantity, is_paid, status, branch_id) "
               "VALUES ($1, $2, $3, $4, $5, $6) RETURNING *")
        return await self.execute(sql, user_id, total_price, quantity, is_paid, status, branch_id, fetchrow=True)

    async def add_order_product(self, order_id: int, product_id: int, price: decimal.Decimal, quantity: int):
        sql = "INSERT INTO order_products (order_id, product_id, price, quantity) VALUES ($1, $2, $3, $4) RETURNING *"
        return await self.execute(sql, order_id, product_id, price, quantity, fetchrow=True)

    async def select_order_products(self, **kwargs):
        sql = "SELECT * FROM order_products WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_orders(self, **kwargs):
        sql = "SELECT * FROM orders WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_order(self, **kwargs):
        sql = "SELECT * FROM orders WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_branches(self):
        sql = "SELECT * FROM branches"
        return await self.execute(sql, fetch=True)

    async def get_branch(self, **kwargs):
        sql = "SELECT * FROM branches WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def update_order_status(self, order_id: int, status: str):
        sql = "UPDATE orders SET status = $2 WHERE id = $1 AND status != 'canceled'"
        return await self.execute(sql, order_id, status, execute=True)

    async def add_chat(self, chat_id: int):
        sql = "INSERT INTO chats (chat_id) VALUES($1) RETURNING *"
        return await self.execute(sql, chat_id, fetchrow=True)

    async def get_chats(self):
        sql = "SELECT * FROM chats"
        return await self.execute(sql, fetch=True)

    async def get_chat(self, **kwargs):
        sql = "SELECT * FROM chats WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_chat_order_messages(self, **kwargs):
        sql = "SELECT * FROM chat_order_messages WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_chat_order_message(self, **kwargs):
        sql = "SELECT * FROM chat_order_messages WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def add_chat_order_message(self, chat_id: int, order_id: int, message_id: int):
        sql = "INSERT INTO chat_order_messages (chat_id, order_id, message_id) VALUES ($1, $2, $3) RETURNING *"
        return await self.execute(sql, chat_id, order_id, message_id, fetchrow=True)
