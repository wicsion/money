from django import forms
from .models import DeveloperProfile

class DeveloperProfileForm(forms.ModelForm):
    class Meta:
        model = DeveloperProfile
        fields = ['company_name', 'description', 'year_founded', 'projects_completed', 'logo']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }