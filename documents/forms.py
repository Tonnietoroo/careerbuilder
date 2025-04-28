from django import forms
from .models import CV, CoverLetter, CVTemplate
from interviews.models import InterviewPrep
from .choices import CERTIFICATION_CHOICES


class CVForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Give your CV a title for easy reference"
    )
    
    # Personal Information
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    # Bio Data
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    nationality = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Personal Profile
    personal_profile = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        help_text="Write a brief professional summary about yourself"
    )
    
    # Responsibilities
    responsibilities = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text="Enter your general responsibilities",
        required=False  # Make it optional if you prefer
    )
    
    # Referee fields
    referee_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    referee_job = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Current Job Title'
    )
    referee_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False
    )
    referee_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = CV
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
        }

class WorkExperienceForm(forms.Form):
    job_title = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    current_job = forms.BooleanField(required=False)
    responsibilities = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))

class EducationForm(forms.Form):
    degree = forms.CharField(max_length=100)
    institution = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    grade = forms.CharField(max_length=20)

class SkillForm(forms.Form):
    skill_name = forms.CharField(max_length=50)
    skill_type = forms.ChoiceField(choices=[('hard', 'Hard Skill'), ('soft', 'Soft Skill')])

class CertificationForm(forms.Form):
    certificate_choice = forms.ChoiceField(
        choices=CERTIFICATION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'certificate_choice'
        })
    )
    custom_certificate = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'custom_certificate',
            'placeholder': 'Enter custom certification name',
            'style': 'display: none;'
        })
    )
    issuing_organization = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    date_earned = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

class LanguageForm(forms.Form):
    PROFICIENCY_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('fluent', 'Fluent'),
        ('native', 'Native')
    ]
    language = forms.CharField(max_length=50)
    proficiency = forms.ChoiceField(choices=PROFICIENCY_CHOICES)

class HobbyForm(forms.Form):
    hobby = forms.CharField(max_length=100)

class CoverLetterForm(forms.ModelForm):
    cv = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    company_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    
    class Meta:
        model = CoverLetter
        fields = ['cv', 'job_title', 'company_name', 'company_address']
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cv'].queryset = CV.objects.filter(user=user)

class InterviewPrepForm(forms.ModelForm):
    job_title = forms.CharField(max_length=200)
    company_name = forms.CharField(max_length=200)
    interview_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = InterviewPrep
        fields = ['job_title', 'company_name', 'interview_date'] 