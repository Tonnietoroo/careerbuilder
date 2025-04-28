from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'phone_number',
            'profile_picture',
            'address',
            'bio',
            'job_title',
            'company',
            'industry',
            'years_of_experience',
            'linkedin',
            'github',
            'portfolio',
            'preferred_job_type',
            'preferred_location',
            'expected_salary',
            'availability_status',
            'remote_work',
            'resume_privacy'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'remote_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
