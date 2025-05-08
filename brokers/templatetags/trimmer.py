from django import template

register = template.Library()

@register.filter(name='trim')
def trim(value):
    print("Trim filter called!")  # Проверьте вывод в консоли
    return value.strip() if value else value