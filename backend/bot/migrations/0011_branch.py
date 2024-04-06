# Generated by Django 5.0.3 on 2024-04-03 06:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0010_alter_product_quantity_order"),
    ]

    operations = [
        migrations.CreateModel(
            name="Branch",
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
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Filial",
                "verbose_name_plural": "Filiallar",
                "db_table": "branches",
            },
        ),
    ]
