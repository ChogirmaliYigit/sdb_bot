# Generated by Django 5.0.3 on 2024-03-29 05:30

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TelegramUser",
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
                (
                    "full_name",
                    models.CharField(
                        blank=True,
                        max_length=500,
                        null=True,
                        verbose_name="To'liq ismi",
                    ),
                ),
                ("username", models.CharField(blank=True, max_length=500, null=True)),
                (
                    "telegram_id",
                    models.BigIntegerField(unique=True, verbose_name="Telegram ID"),
                ),
                ("phone_number", models.CharField(verbose_name="Telefon raqami", max_length=20, null=True, blank=True))
            ],
            options={
                "verbose_name": "Telegram Foydalanuvchi",
                "verbose_name_plural": "Telegram Foydalanuvchilar",
                "db_table": "telegram_users",
                "unique_together": ("telegram_id", "phone_number"),
            },
        ),
    ]
