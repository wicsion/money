from django import template
from accounts.models import Favorite  # Или правильный путь к модели

register = template.Library()

@register.filter(name='is_broker_favorite')
def is_broker_favorite(user, broker_user):
    return Favorite.objects.filter(
        user=user,
        broker=broker_user,
        favorite_type='broker'
    ).exists()