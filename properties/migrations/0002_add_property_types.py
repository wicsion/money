from django.db import migrations

def add_property_types(apps, schema_editor):
    PropertyType = apps.get_model('properties', 'PropertyType')
    types = [
        ('Квартира в новостройке', 'Новостройка с современной планировкой'),
        ('Квартира на вторичке', 'Вторичное жилье'),
        ('Нежилое помещение', 'Офисы, склады, торговые площади')
    ]
    for name, desc in types:
        PropertyType.objects.get_or_create(name=name, description=desc)

class Migration(migrations.Migration):
    dependencies = [
        ('properties', '0001_initial'),  # Укажите имя вашей первой миграции
    ]
    operations = [
        migrations.RunPython(add_property_types),
    ]