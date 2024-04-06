from decimal import Decimal


def make_title(title):
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    name = ""
    for letter in title:
        if letter in escape_chars:
            name += f'\{letter}'
        else:
            name += letter
    return name


async def calculate_discount_price(product) -> tuple:
    original_price = product.get('price')
    discount_percentage = Decimal(product.get('discount_percentage'))
    discount_price = round(original_price - (original_price * (discount_percentage / 100)), 1)
    return round(original_price, 1), discount_percentage, discount_price
