import django_filters
from .models import Property, PropertyType


class PropertyFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_area = django_filters.NumberFilter(field_name='area', lookup_expr='gte')
    max_area = django_filters.NumberFilter(field_name='area', lookup_expr='lte')
    rooms = django_filters.NumberFilter(field_name='rooms')
    property_type = django_filters.ModelChoiceFilter(queryset=PropertyType.objects.all())

    class Meta:
        model = Property
        fields = ['property_type', 'rooms', 'location']