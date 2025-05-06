from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _



class PropertyType(models.Model):
    name = models.CharField(
            max_length=100,
            choices=[
                ('new_flat', 'Квартира в новостройке'),
                ('resale_flat', 'Квартира на вторичке'),
                ('commercial', 'Нежилое помещение'),
                ('house', 'Дом')  # Добавлен новый тип
            ],
            unique=True,
            verbose_name='Тип объекта'
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Название иконки из FontAwesome')
    )

    class Meta:
        verbose_name = _('Тип недвижимости')
        verbose_name_plural = _('Типы недвижимости')
        ordering = ['name']

    def __str__(self):
        return self.name




class Property(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Активно')
        SOLD = 'sold', _('Продано')
        ARCHIVED = 'archived', _('В архиве')

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Заголовок')
    )
    description = models.TextField(
        verbose_name=_('Описание')
    )
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.PROTECT,
        verbose_name=_('Тип недвижимости')
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_('Цена')
    )
    area = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_('Площадь (м²)')
    )
    rooms = models.PositiveIntegerField(
        verbose_name=_('Количество комнат')
    )
    location = models.CharField(
        max_length=200,
        verbose_name=_('Расположение')
    )
    address = models.TextField(
        verbose_name=_('Полный адрес')
    )
    main_image = models.ImageField(
        upload_to='properties/',
        verbose_name=_('Главное изображение')
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('Статус')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Дата обновления')
    )
    broker = models.ForeignKey(
    'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broker_properties',
        verbose_name=_('Брокер')
    )
    developer = models.ForeignKey(
    'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='developer_properties',
        verbose_name = _('Застройщик')
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name=_('Премиум')
    )
    is_hot = models.BooleanField(
        default=False,
        verbose_name=_('Горячее предложение')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Одобрено')
    )
    floor = models.PositiveIntegerField(
        verbose_name=_('Этаж'),  # Убраны blank=True и null=True
        blank=True,  # Добавлено
        null=True,
        validators=[MinValueValidator(1)]  # Добавлена валидация
    )
    apartment_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('studio', 'Студия'),
            ('apartment', 'Апартаменты'),
            ('regular', 'Обычная квартира'),
        ],
        verbose_name=_('Тип квартиры')
    )
    class Meta:
        verbose_name = _('Объект недвижимости')
        verbose_name_plural = _('Объекты недвижимости')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.price} ₽"

    def get_status_color(self):
        colors = {
            'active': 'green',
            'sold': 'red',
            'archived': 'gray'
        }
        return colors.get(self.status, 'blue')

    def save(self, *args, **kwargs):
        if self.property_type.name in ['new_flat', 'resale_flat']:
            type_map = {
                'studio': 'Студия',
                'apartment': 'Апартаменты',
                'regular': f'{self.rooms}-к. квартира'
            }
            self.title = f"{type_map.get(self.apartment_type, 'Квартира')}, {self.area} м², {self.floor} этаж"
        elif self.property_type.name == 'house':
            self.title = f"Дом, {self.area} м²"
        else:
            # Используем get_name_display() из PropertyType
            self.title = f"{self.property_type.get_name_display()}, {self.area} м²"

        super().save(*args, **kwargs)


class PropertyImage(models.Model):
    """Дополнительные изображения объекта"""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Объект')
    )
    image = models.ImageField(
        upload_to='property_images/',
        verbose_name=_('Изображение')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Порядок')
    )

    class Meta:
        verbose_name = _('Изображение объекта')
        verbose_name_plural = _('Изображения объектов')
        ordering = ['order']

    def __str__(self):
        return f"Изображение для {self.property.title}"


class Favorite(models.Model):
    """Избранные объекты пользователей"""
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь')
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('Объект')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата добавления')
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранные объекты')
        unique_together = ('user', 'property')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} → {self.property}"


