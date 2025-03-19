from django import forms
from django.utils import timezone
from .models import InterviewPrep, InterviewQuestion, Industry

class InterviewPrepForm(forms.ModelForm):
    interview_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    class Meta:
        model = InterviewPrep
        fields = ['job_title', 'company_name', 'interview_date', 'notes']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_interview_date(self):
        date = self.cleaned_data['interview_date']
        if date < timezone.now().date():
            raise forms.ValidationError("Interview date cannot be in the past")
        return date

class QuestionForm(forms.ModelForm):
    class Meta:
        model = InterviewQuestion
        fields = ['question_type', 'question', 'answer']
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 4}),
        }

class IndustryForm(forms.ModelForm):
    class Meta:
        model = Industry
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        } 