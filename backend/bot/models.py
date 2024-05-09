import requests
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


class TelegramUser(models.Model):
    full_name = models.CharField(verbose_name="To'liq ismi", max_length=500, null=True, blank=True)
    telegram_id = models.BigIntegerField(verbose_name="Telegram ID", unique=True)
    phone_number = models.CharField(verbose_name="Telefon raqami", max_length=20, null=True, blank=True)

    def __str__(self): return self.full_name or f"Foydalanuvchi - {self.telegram_id}"

    class Meta:
        db_table = "telegram_users"
        verbose_name = "Telegram Foydalanuvchi"
        verbose_name_plural = "Telegram Foydalanuvchilar"
        unique_together = ("telegram_id", "phone_number", )


class Category(models.Model):
    name = models.CharField(verbose_name="Nomi", max_length=300)
    description = models.TextField(verbose_name="Qo'shimcha ma'lumoti", null=True, blank=True)
    image = models.ImageField(verbose_name="Rasmi", upload_to="categories/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "categories"
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


class Product(models.Model):
    name = models.CharField(verbose_name="Nomi", max_length=300)
    description = models.TextField(verbose_name="Qo'shimcha ma'lumoti", null=True, blank=True)
    price = models.DecimalField(verbose_name="Narxi", max_digits=20, decimal_places=2, validators=[MinValueValidator(0)])
    discount_percentage = models.FloatField(verbose_name="Chegirma foizi (%)", default=0.00)
    quantity = models.PositiveIntegerField(verbose_name="Soni", default=0, validators=[MinValueValidator(0)])
    image = models.ImageField(verbose_name="Rasmi", upload_to="products/", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self): return self.name

    class Meta:
        db_table = "products"
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"


class Cart(models.Model):
    user = models.ForeignKey(verbose_name="Foydalanuvchi", to=TelegramUser, on_delete=models.CASCADE)
    product = models.ForeignKey(verbose_name="Mahsulot", to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Soni", validators=[MinValueValidator(1)])

    def __str__(self): return f"{self.user.full_name} - {self.product.name}"

    class Meta:
        db_table = "carts"
        verbose_name = "Savat"
        verbose_name_plural = "Savatlar"


class Order(models.Model):
    IN_PROCESSING = "in_processing"
    CONFIRMED = "confirmed"
    SUCCESS = "success"
    CANCELED = "canceled"
    PAYMENT_CANCELED = "payment_canceled"
    REFUNDED = "refunded"

    STATUSES = (
        (IN_PROCESSING, "Jarayonda"),
        (CONFIRMED, "Tasdiqlangan"),
        (SUCCESS, "Muvaffaqiyatli"),
        (CANCELED, "Bekor qilingan"),
        (PAYMENT_CANCELED, "To'lov bekor qilingan"),
        (REFUNDED, "Qaytarilgan"),
    )

    user = models.ForeignKey(verbose_name="Mijoz", to=TelegramUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(verbose_name="To'liq narxi", max_digits=20, decimal_places=2)
    quantity = models.PositiveIntegerField(verbose_name="Soni", validators=[MinValueValidator(1)])
    is_paid = models.BooleanField(verbose_name="To'lov holati", default=False)
    status = models.CharField(verbose_name="Holati", max_length=20, choices=STATUSES, default=IN_PROCESSING)
    branch = models.ForeignKey(
        verbose_name="Filial", to="Branch", on_delete=models.PROTECT, null=True, blank=True,
        help_text="Mijoz buyurtmani olib ketishi kerak bo'lgan filial."
    )

    def __str__(self):
        return f"#{self.pk} raqamli buyurtma ({self.user.full_name})"

    @property
    def payment_status(self):
        return "To'langan✅" if self.is_paid else "To'lanmagan❌"

    class Meta:
        db_table = "orders"
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


class OrderProduct(models.Model):
    order = models.ForeignKey(verbose_name="Buyurtma", to=Order, on_delete=models.CASCADE)
    product = models.ForeignKey(verbose_name="Mahsulot", to=Product, on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name="Narxi", max_digits=20, decimal_places=2)
    quantity = models.PositiveIntegerField(verbose_name="Soni", validators=[MinValueValidator(1)])

    def __str__(self):
        return f"#{self.order.id} raqamli buyurtmaning mahsulotlari"

    class Meta:
        db_table = "order_products"
        verbose_name = "Buyurtma mahsuloti"
        verbose_name_plural = "Buyurtma mahsulotlari"


class Branch(models.Model):
    name = models.CharField(verbose_name="Nomi", max_length=300)
    latitude = models.FloatField(verbose_name="Kenglik")
    longitude = models.FloatField(verbose_name="Uzunlik")
    description = models.TextField(verbose_name="Qo'shimcha", null=True, blank=True, help_text="Misol uchun: Mo'ljal")

    def __str__(self): return self.name

    class Meta:
        db_table = "branches"
        verbose_name = "Filial"
        verbose_name_plural = "Filiallar"


class Chat(models.Model):
    chat_id = models.BigIntegerField(verbose_name="Chat ID (telegram)", unique=True)

    def __str__(self): return str(self.chat_id)

    class Meta:
        db_table = "chats"
        verbose_name = "Chat"
        verbose_name_plural = "Chatlar"


class ChatOrderMessage(models.Model):
    chat = models.ForeignKey(verbose_name="Chat", to=Chat, on_delete=models.CASCADE)
    order = models.ForeignKey(verbose_name="Buyurtma", to=Order, on_delete=models.CASCADE)
    message_id = models.BigIntegerField(verbose_name="Xabar ID (Telegram)")

    class Meta:
        db_table = "chat_order_messages"


@receiver(post_save, sender=Order)
def change_chat_message(sender, **kwargs):
    order = kwargs.get("instance")
    order_statuses = {
        "in_processing": "Jarayonda",
        "confirmed": "Tasdiqlangan",
        "success": "Muvaffaqiyatli",
        "canceled": "Bekor qilingan",
        "payment_canceled": "To'lov bekor qilingan",
        "refunded": "Qaytarilgan",
    }
    payment_status = "To'langan✅" if order.is_paid else "To'lanmagan❌"
    branch = Branch.objects.get(id=order.branch_id)
    order_products = OrderProduct.objects.filter(order=order)
    product_names = []
    for order_product in order_products:
        product_names.append(order_product.product.name)

    text = (f"<b>№{order.pk} raqamli buyurtma:</b>\n\n"
            f"📱Telefon raqam: {order.user.phone_number}\n"
            f"📦Holati: <u>{order_statuses.get(order.status)}</u>\n"
            f"💸To'lov holati: {payment_status}\n"
            f"🏢Filial: {branch.name}\n"
            f"📋Mahsulotlar: <b>{', '.join(product_names)}</b>\n\n"
            f"<b>💸Umumiy narx: {order.total_price} so'm</b>")

    chat_order_messages = ChatOrderMessage.objects.filter(order=order)
    for chat_order_message in chat_order_messages:
        try:
            requests.post(
                url=f"https://api.telegram.org/bot{settings.BOT_TOKEN}/editMessageText",
                data={
                    "chat_id": chat_order_message.chat.chat_id,
                    "message_id": chat_order_message.message_id,
                    "text": text,
                    "parse_mode": "html",
                },
            )
        except Exception as err:
            print(err)
