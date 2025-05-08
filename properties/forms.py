from django import forms
from .models import Property, PropertyImage


class PropertyForm(forms.ModelForm):
    apartment_type = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('studio', 'Студия'),
            ('apartment', 'Апартаменты'),


        ],
        required=False,
        label='Тип квартиры'
    )

    floor = forms.IntegerField(
        required=False,
        label='Этаж',
        min_value=1
    )

    total_floors = forms.IntegerField(
        required=False,
        label='Всего этажей в доме',
        min_value=1,
        help_text='Укажите общее количество этажей в доме'
    )
    rooms = forms.IntegerField(
        label='Количество комнат',
        min_value=1,
        required=True  # Явно указываем обязательность
    )

    class Meta:
        model = Property
        fields = [
            'description', 'price', 'status', 'broker',
            'developer', 'is_premium', 'main_image',
            'rooms', 'location', 'address',
            'apartment_type', 'floor', 'total_floors', 'has_finishing',
            'delivery_year',
            'is_delivered',
            'living_area',
            'total_area',
            'metro_station'
        ]
        widgets = {
            'status': forms.HiddenInput(),
            'broker': forms.HiddenInput(),
            'developer': forms.HiddenInput(),
            'is_premium': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'has_finishing': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_delivered': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        }

    def __init__(self, *args, **kwargs):
        # Извлекаем property_type перед вызовом super()
        self.property_type = kwargs.pop('property_type', None)
        super().__init__(*args, **kwargs)

        # Устанавливаем начальные значения
        self.fields['status'].initial = 'active'
        self.fields['is_premium'].initial = False

        # Управление полями в зависимости от типа
        if self.property_type and self.property_type.name in ['new_flat', 'resale_flat']:
            self.fields['floor'].required = True
        else:
            self.fields.pop('apartment_type', None)
            self.fields.pop('floor', None)

    def clean(self):
        cleaned_data = super().clean()
        required_fields = {
            'rooms': 'Укажите количество комнат',
            'total_area': 'Укажите общую площадь',
            'price': 'Укажите цену объекта',
            'location': 'Укажите расположение',
        }
        floor = cleaned_data.get('floor')
        total_floors = cleaned_data.get('total_floors')

        for field, error_msg in required_fields.items():
            if not cleaned_data.get(field):
                self.add_error(field, error_msg)

        if floor and total_floors:
            if floor > total_floors:
                self.add_error('floor', 'Этаж квартиры не может превышать общее количество этажей')

        return cleaned_data

    def clean_main_image(self):
        image = self.cleaned_data.get('main_image')
        if not image:
            raise forms.ValidationError("Главное изображение обязательно")
        return image

class PropertyImageForm(forms.ModelForm):
    images = forms.FileField(
        label='Дополнительные фото (до 10)',
        required=False,
        widget=forms.FileInput()
    )

    class Meta:
        model = PropertyImage
        fields = ['images']