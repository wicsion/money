# Generated by Django 5.2 on 2025-06-13 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_alter_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
