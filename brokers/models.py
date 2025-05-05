from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from properties.models import Property



class BrokerProfile(models.Model):
    """Профиль брокера недвижимости"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='broker_profile',
        verbose_name=_('Пользователь')
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Номер лицензии')
    )
    experience = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Опыт работы (лет)')
    )
    specialization = models.CharField(
        max_length=200,
        verbose_name=_('Специализация')
    )
    about = models.TextField(
        verbose_name=_('О себе'),
        blank=True
    )
    avatar = models.ImageField(  # Добавлено новое поле
        upload_to='broker_avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар')
    )

    is_archived = models.BooleanField(
        default=False,
        verbose_name=_('В архиве')
    )
    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата архивации')
    )
    subscription_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Окончание подписки')
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        verbose_name=_('Рейтинг')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Подтвержден')
    )

    class Meta:
        verbose_name = _('Профиль брокера')
        verbose_name_plural = _('Профили брокеров')
        ordering = ['-rating']

    def __str__(self):
        return f"{self.user.get_full_name()} (Лицензия: {self.license_number})"

    def active_properties(self):
        return self.user.broker_properties.filter(status='active', is_approved=True)

    active_properties.short_description = _('Активные объекты')


class BrokerReview(models.Model):
    """Отзывы о брокерах"""

    broker = models.ForeignKey(
        BrokerProfile,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Брокер')
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Клиент')
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_('Оценка')
    )
    comment = models.TextField(
        verbose_name=_('Комментарий')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Одобрен')
    )

    class Meta:
        verbose_name = _('Отзыв о брокере')
        verbose_name_plural = _('Отзывы о брокерах')
        ordering = ['-created_at']
        unique_together = ('broker', 'client')

    def __str__(self):
        return f"Отзыв {self.client} для {self.broker} ({self.rating}/5)"



class ContactRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('completed', 'Завершено')
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brokers_sent_requests' )
    broker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brokers_received_requests')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='brokers_contact_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    transaction_id = models.CharField(max_length=100, blank=True)