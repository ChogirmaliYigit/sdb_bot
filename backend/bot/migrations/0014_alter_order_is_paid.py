# Generated by Django 5.0.3 on 2024-04-03 14:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0013_remove_order_product_order_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="is_paid",
            field=models.BooleanField(default=False, verbose_name="To'lov holati"),
        ),
    ]
