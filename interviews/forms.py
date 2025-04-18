from django import forms
from django.utils import timezone
from datetime import datetime
from .models import InterviewPrep, InterviewQuestion, Industry

class InterviewPrepForm(forms.ModelForm):
    interview_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )
    
    industry = forms.ModelChoiceField(
        queryset=Industry.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = InterviewPrep
        fields = ['industry', 'job_title', 'company_name', 'interview_date', 'notes']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_interview_date(self):
        date = self.cleaned_data.get('interview_date')
        if not date:
            return None
            
        # Always make the date timezone-aware in the current timezone
        if timezone.is_naive(date):
            date = timezone.make_aware(date)
            
        # Convert to the current timezone if it's in a different timezone
        return timezone.localtime(date)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = InterviewQuestion
        fields = ['question_type', 'question', 'answer', 'industry']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'industry': forms.Select(attrs={'class': 'form-control'})
        }

class IndustryForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
