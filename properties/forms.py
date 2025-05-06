from django import forms
from .models import Property, PropertyImage

class PropertyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'active'  # Установите значение по умолчанию
        self.fields['is_premium'].initial = False
        self.fields['apartment_type'].required = False

    class Meta:
        model = Property
        fields = [
            'title', 'description', 'price', 'property_type',
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


class PropertyImageForm(forms.ModelForm):
    images = forms.FileField(
        label='Дополнительные фото (до 10)',
        required=False,
        widget=forms.FileInput()  # Убраны атрибуты multiple
    )

    class Meta:
        model = PropertyImage
        fields = ['images']