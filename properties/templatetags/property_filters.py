from django import template

register = template.Library()

@register.filter
def space_format(value):
    return "{:,.0f}".format(value).replace(",", " ").replace(".", " ")