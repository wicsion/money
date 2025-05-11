from datetime import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from properties.models import Property

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('Phone Number'), max_length=18, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=150, blank=True)
    experience = models.IntegerField(
        _('Experience'),
        null=True,
        blank=True,
        help_text="Опыт работы в годах (только для брокеров)"
    )
    license_number = models.CharField(
        _('License Number'),
        max_length=50,
        null=True,
        blank=True,
        help_text="Номер лицензии (только для брокеров)"
    )

    verification_token = models.CharField(max_length=100, blank=True, null=True, verbose_name='Токен верификации')

    @property
    def is_profile_complete(self):
        if self.user_type == User.UserType.BROKER:
            # Проверка для брокеров
            has_broker_profile = (
                    hasattr(self, 'broker_profile') and
                    self.broker_profile.license_number and
                    self.broker_profile.experience is not None
            )
            return (
                    has_broker_profile and
                    self.last_name and
                    self.first_name and
                    self.phone and
                    self.passport
            )
        else:
            # Проверка для клиентов и застройщиков
            return all([
                self.user_type,
                self.last_name and self.last_name.strip() != '',
                self.first_name and self.first_name.strip() != '',
                self.phone and self.phone.strip() != '',
                self.passport and self.passport.strip() != ''
            ])

    class UserType(models.TextChoices):
        CLIENT = 'client', _('Client')
        BROKER = 'broker', _('Broker')
        DEVELOPER = 'developer', _('Developer')

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        verbose_name=_('User Type')
    )

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('Avatar'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    passport = models.CharField(_('Passport Data'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}".strip()

    @property
    def is_client(self):
        return self.user_type == self.UserType.CLIENT

    @property
    def is_broker(self):
        return self.user_type == self.UserType.BROKER

    @property
    def is_developer(self):
        return self.user_type == self.UserType.DEVELOPER



    @property
    def days_remaining(self):
        return (self.end_date - timezone.now()).days


class UserActivity(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активности пользователей'

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    developer = models.ForeignKey(
        'developers.DeveloperProfile',
        on_delete=models.CASCADE
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'developer')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"{self.user} → {self.developer}"





class Favorite(models.Model):
    FAVORITE_TYPES = [
        ('client', 'Клиентский'),
        ('broker', 'Брокерский')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'account_favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, default=1 )

    broker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='broker_favorites'  # Добавьте это поле
    )

    favorite_type = models.CharField(
        max_length=10,
        choices=FAVORITE_TYPES,
        default='client'
    )
    created_at = models.DateTimeField(auto_now_add=True)



class ContactRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В обработке'),
        ('completed', 'Завершен'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts_sent_requests')
    broker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts_received_requests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='accounts_contact_requests' )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Запрос #{self.id} от {self.requester}"

class Message(models.Model):
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    contact_request = models.ForeignKey(ContactRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(
        upload_to='chat_attachments/',
        null=True,
        blank=True,
        verbose_name='Вложение'
    )
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Сообщение от {self.sender} в запросе #{self.contact_request.id}"


class DeveloperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_developer_profile')
    company = models.CharField(max_length=255, verbose_name='Компания')
    description = models.TextField(verbose_name='Описание')
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')

    def __str__(self):
        return f"Профиль застройщика: {self.company}"


class BrokerSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('expired', 'Истекла'),
        ('canceled', 'Отменена')
    ]

    broker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='broker_subscriptions')
    developer = models.ForeignKey(DeveloperProfile, on_delete=models.CASCADE, related_name='subscribers')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payment = models.OneToOneField('payments.Payment', on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('broker', 'developer')

    @property
    def is_active(self):
        return self.status == 'active' and self.end_date >= timezone.now()


class ExclusiveProperty(Property):

    is_exclusive = models.BooleanField(default=True)
    subscription_required = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Эксклюзивный объект'
        verbose_name_plural = 'Эксклюзивные объекты'


class PropertyListing(models.Model):
    broker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_featured = models.BooleanField(default=False)
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

class StatusLog(models.Model):
    contact_request = models.ForeignKey(ContactRequest, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20, choices=ContactRequest.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_status_display()} - {self.timestamp.strftime('%d.%m.%Y %H:%M')}"

