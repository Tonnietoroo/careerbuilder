from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profiles_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Professional Info
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    skills = models.JSONField(default=list)
    
    # Social Links
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    
    # Career Preferences
    job_type_choices = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship')
    ]
    preferred_job_type = models.CharField(max_length=20, choices=job_type_choices, blank=True)
    preferred_location = models.CharField(max_length=100, blank=True)
    remote_work = models.BooleanField(default=False)
    expected_salary = models.CharField(max_length=50, blank=True)
    
    # New fields
    availability_status = models.CharField(
        max_length=20,
        choices=[
            ('actively_looking', 'Actively Looking'),
            ('open', 'Open to Opportunities'),
            ('not_looking', 'Not Looking')
        ],
        default='open'
    )
    
    resume_privacy = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('connections', 'Connections Only')
        ],
        default='private'
    )
    
    notification_preferences = models.JSONField(
        default=dict,
        help_text="Notification settings for the user"
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            'phone_number', 'address', 'bio', 'profile_picture',
            'job_title', 'company', 'industry', 'skills',
            'linkedin', 'github', 'portfolio'
        ]
        
        filled_fields = sum(1 for field in fields_to_check if getattr(self, field))
        return int((filled_fields / len(fields_to_check)) * 100)

class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class SkillEndorsement(TimeStampedModel):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    endorsed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['skill', 'profile', 'endorsed_by']

class Education(TimeStampedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

class WorkExperience(TimeStampedModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField()
