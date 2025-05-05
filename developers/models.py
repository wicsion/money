from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class DeveloperProfile(models.Model):
    """Профиль застройщика"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='developer_profile',
        verbose_name=_('Пользователь')
    )
    company_name = models.CharField(
        max_length=200,
        verbose_name=_('Название компании')
    )
    description = models.TextField(
        verbose_name=_('Описание компании'),
        blank=True
    )
    year_founded = models.PositiveIntegerField(
        verbose_name=_('Год основания')
    )
    projects_completed = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Завершенных проектов')
    )
    logo = models.ImageField(
        upload_to='developer_logos/',
        blank=True,
        null=True,
        verbose_name=_('Логотип')
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Подтвержден')
    )

    class Meta:
        verbose_name = _('Профиль застройщика')
        verbose_name_plural = _('Профили застройщиков')
        ordering = ['company_name']

    def __str__(self):
        return self.company_name

    def active_projects(self):
        return self.user.developer_properties.filter(status='active', is_approved=True)

    active_projects.short_description = _('Активные проекты')