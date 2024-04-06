from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TelegramUser, Category, Product, Cart, Order, OrderProduct, Branch, Chat


@admin.register(TelegramUser)
class TelegramUserAdmin(ModelAdmin):
    list_display = (
        "full_name",
        "phone_number",
        "telegram_id",
    )
    fields = (
        "full_name",
        "phone_number",
        "telegram_id",
    )
    search_fields = (
        "id",
        "full_name",
        "telegram_id",
        "phone_number",
    )


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "parent", )
    fields = ("name", "description", "image", "parent",)
    search_fields = ("name", "description", "id", "parent",)
    list_filter = ("parent", )
    list_filter_submit = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Category.objects.filter(parent__isnull=True)  # Filter top-level categories
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "description", "price", )
    fields = ("category", "name", "description", "price", "discount_percentage", "quantity", "image", )
    search_fields = ("name", "description", "price", )
    ordering = ("price", "discount_percentage", "quantity", )
    list_filter = ("category", )
    list_filter_submit = True


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ("product", "user", "quantity",)
    fields = list_display
    search_fields = list_display


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("user", "total_price", "payment_status", "status",)
    fields = ("user", "total_price", "quantity", "is_paid", "status", "branch",)
    list_filter = ("is_paid", "status", "branch",)
    search_fields = ("user", "total_price", "quantity", "branch", "status",)
    list_filter_submit = True


@admin.register(OrderProduct)
class OrderProductAdmin(ModelAdmin):
    list_display = ("order", "product", "price", "quantity",)
    fields = list_display
    list_filter = ("order",)
    search_fields = list_display


@admin.register(Branch)
class BranchAdmin(ModelAdmin):
    list_display = ("name",)
    fields = ("name", "latitude", "longitude", "description",)
    search_fields = fields


@admin.register(Chat)
class ChatAdmin(ModelAdmin):
    list_display = ("chat_id",)
    fields = list_display
    search_fields = list_display
