# Generated by Django 5.2 on 2025-06-12 22:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BrokerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license_number', models.CharField(max_length=50, unique=True, verbose_name='Номер лицензии')),
                ('experience', models.PositiveIntegerField(default=0, verbose_name='Опыт работы (лет)')),
                ('about', models.TextField(blank=True, verbose_name='О себе')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='broker_avatars/', verbose_name='Аватар')),
                ('is_archived', models.BooleanField(default=False, verbose_name='В архиве')),
                ('archived_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата архивации')),
                ('subscription_expiry', models.DateField(blank=True, null=True, verbose_name='Окончание подписки')),
                ('rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3, verbose_name='Рейтинг')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Подтвержден')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='broker_profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Профиль брокера',
                'verbose_name_plural': 'Профили брокеров',
                'ordering': ['-rating'],
            },
        ),
        migrations.CreateModel(
            name='BrokerReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Оценка')),
                ('comment', models.TextField(verbose_name='Комментарий')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_approved', models.BooleanField(default=False, verbose_name='Одобрен')),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='brokers.brokerprofile', verbose_name='Брокер')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
                ('contact_request', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='br_contact_request', to='accounts.contactrequest')),
            ],
            options={
                'verbose_name': 'Отзыв о брокере',
                'verbose_name_plural': 'Отзывы о брокерах',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ContactRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Ожидает оплаты'), ('paid', 'Оплачено'), ('completed', 'Завершено')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('payment_amount', models.DecimalField(decimal_places=2, default=10.0, max_digits=10)),
                ('transaction_id', models.CharField(blank=True, max_length=100)),
                ('is_consultation', models.BooleanField(default=False)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brokers_received_requests', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
