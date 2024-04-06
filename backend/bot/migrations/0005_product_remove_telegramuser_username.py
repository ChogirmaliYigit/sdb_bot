# Generated by Django 5.0.3 on 2024-03-29 10:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0004_alter_brand_name_remove_category_brand_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                ("name", models.CharField(max_length=300)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=20,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("discount_percentage", models.FloatField(default=0.0)),
                ("quantity", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Mahsulot",
                "verbose_name_plural": "Mahsulotlar",
                "db_table": "products",
            },
        ),
        migrations.RemoveField(
            model_name="telegramuser",
            name="username",
        ),
    ]