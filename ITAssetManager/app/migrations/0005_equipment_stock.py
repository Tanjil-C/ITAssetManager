# Generated by Django 4.1.5 on 2024-09-11 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_employee_hire_date_employee_position_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
