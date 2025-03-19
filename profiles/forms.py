from django import forms
from .models import Profile, Education, WorkExperience

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.SelectMultiple(attrs={'class': 'select2'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['profile', 'created_at', 'updated_at']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        exclude = ['profile', 'created_at', 'updated_at']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        } 