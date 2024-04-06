from django.db import migrations


def add_unique_constraint(apps, schema_editor):
    User = apps.get_model('bot', 'TelegramUser')
    constraint_name = 'unique_non_null_phone_number'
    schema_editor.execute(
        f'CREATE UNIQUE INDEX {constraint_name} ON {User._meta.db_table} (phone_number) WHERE phone_number IS NOT NULL;'
    )


def remove_unique_constraint(apps, schema_editor):
    User = apps.get_model('bot', 'TelegramUser')
    constraint_name = 'unique_non_null_phone_number'
    schema_editor.execute(
        f'DROP INDEX {User._meta.db_table}_{constraint_name}'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001__initial'),
    ]

    operations = [
        migrations.RunPython(add_unique_constraint, remove_unique_constraint)
    ]
