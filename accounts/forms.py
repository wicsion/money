from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from .models import User, ContactRequest, Property


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'last_name',
                  'first_name', 'patronymic']


class UserAdminChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class RoleSelectionForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=User.UserType.choices,
        widget=forms.RadioSelect(),
        label='Выберите вашу роль',
        required=True
    )

    class Meta:
        model = User
        fields = ['role']  # Только поле роли


        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'phone': 'Телефон',
            'passport': 'Паспортные данные',
            'avatar': 'Аватар'
        }
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 999-99-99'}),
            'passport': forms.TextInput(attrs={'placeholder': '1234 567890'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=18,
        validators=[
            RegexValidator(
                regex=r'^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$',
                message="Номер должен быть в формате: +7 (XXX) XXX-XX-XX"
            )
        ],
        required=True,
        label='Телефон'

    )

    passport = forms.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{4}\s\d{6}$',
                message="Паспорт должен быть в формате: 1234 567890"
            )
        ],
        required=True,
        label='Паспортные данные'
    )

    class Meta:
        model = User
        fields = [
            'last_name',
            'first_name',
            'patronymic',
            'phone',
            'passport',
            'avatar'
        ]
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'patronymic': 'Отчество',
            'phone': 'Телефон',
            'passport': 'Паспортные данные',
            'avatar': 'Фотография профиля'
        }
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 999-99-99'}),
            'passport': forms.TextInput(attrs={'placeholder': '1234 567890'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля обязательными на уровне формы
        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
        self.fields['phone'].required = True
        self.fields['passport'].required = True


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['broker', 'property']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['broker'].queryset = User.objects.filter(user_type=User.UserType.BROKER)
        self.fields['property'].queryset = Property.objects.none()

        if 'broker' in self.data:
            try:
                broker_id = int(self.data.get('broker'))
                self.fields['property'].queryset = Property.objects.filter(creator_id=broker_id)
            except (ValueError, TypeError):
                pass