# Generated by Django 5.0.3 on 2024-04-02 09:32

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0009_cart"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="quantity",
            field=models.PositiveIntegerField(
                default=0,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Soni",
            ),
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=20)),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Soni",
                    ),
                ),
                ("is_paid", models.BooleanField(default=False)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bot.product",
                        verbose_name="Mahsulot",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bot.telegramuser",
                        verbose_name="Foydalanuvchi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Buyurtma",
                "verbose_name_plural": "Buyurtmalar",
                "db_table": "orders",
            },
        ),
    ]
