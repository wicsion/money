from django import forms
from .models import BrokerProfile, BrokerReview

class BrokerProfileForm(forms.ModelForm):
    class Meta:
        model = BrokerProfile
        fields = ['license_number', 'experience', 'specialization', 'about', 'avatar']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
        }

class BrokerReviewForm(forms.ModelForm):
    class Meta:
        model = BrokerReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }