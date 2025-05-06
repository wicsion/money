from django import forms
from .models import Property, PropertyImage, PropertyType


class PropertyForm(forms.ModelForm):
    property_type = forms.ModelChoiceField(
        queryset=PropertyType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Тип объекта'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'active'  # Установите значение по умолчанию
        self.fields['is_premium'].initial = False
        self.fields['apartment_type'].required = False
        self.fields['floor'].required = False
        self.property_type = kwargs.pop('property_type', None)

        if self.property_type and self.property_type.name in ['new_flat', 'resale_flat']:
            self.fields['apartment_type'].required = False
            self.fields['floor'].required = True
        else:
            del self.fields['apartment_type']
            del self.fields['floor']


    apartment_type = forms.ChoiceField(
        choices=[
            ('studio', 'Студия'),
            ('apartment', 'Апартаменты'),
            ('regular', 'Обычная квартира'),  # Добавьте эту строку
        ],
        required=False,
        label='Тип квартиры'
    )

    floor = forms.IntegerField(
        required=False,
        label='Этаж',
        min_value=1
    )








    class Meta:
        model = Property
        fields = [
           'description', 'price',
            'status', 'broker', 'developer', 'is_premium',
            'main_image', 'area', 'rooms', 'location', 'address','apartment_type',
            'floor'
        ]
        widgets = {
            'status': forms.HiddenInput(),  # Скрываем ненужные поля
            'broker': forms.HiddenInput(),
            'developer': forms.HiddenInput(),
            'is_premium': forms.HiddenInput(),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }



    def clean(self):
        cleaned_data = super().clean()
        property_type = cleaned_data.get('property_type')

        # Проверка для квартир
        if property_type and property_type.name in ['new_flat', 'resale_flat']:
            if not cleaned_data.get('floor'):
                self.add_error('floor', 'Укажите этаж для квартиры')

        return cleaned_data

class PropertyImageForm(forms.ModelForm):
    images = forms.FileField(
        label='Дополнительные фото (до 10)',
        required=False,
        widget=forms.FileInput()  # Убраны атрибуты multiple
    )

    class Meta:
        model = PropertyImage
        fields = ['images']