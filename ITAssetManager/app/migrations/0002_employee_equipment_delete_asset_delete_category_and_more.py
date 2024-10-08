# Generated by Django 4.1.5 on 2024-09-10 15:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('acquire_date', models.DateField(blank=True, null=True)),
                ('serial_number', models.CharField(max_length=100, unique=True)),
                ('condition_status', models.CharField(choices=[('new', 'New'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('broken', 'Broken')], default='new', max_length=10)),
                ('usage_status', models.CharField(choices=[('free', 'Free'), ('in_use', 'In Use'), ('maintenance', 'Maintenance'), ('in_repair', 'In Repair')], default='free', max_length=15)),
                ('assigned_users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Asset',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.AddField(
            model_name='employee',
            name='equipment',
            field=models.ManyToManyField(blank=True, to='app.equipment'),
        ),
    ]
