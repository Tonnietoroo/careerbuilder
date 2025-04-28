from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('immediately', 'Immediately'),
        ('1_week', '1 Week'),
        ('2_weeks', '2 Weeks'),
        ('1_month', '1 Month'),
        ('not_available', 'Not Available'),
    ]
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('connections', 'Connections Only'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='accounts_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    
    # Professional Information
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Social Links
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    
    # Career Preferences
    preferred_job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True)
    preferred_location = models.CharField(max_length=100, blank=True)
    expected_salary = models.CharField(max_length=50, blank=True)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, blank=True)
    remote_work = models.BooleanField(default=False)
    
    # Privacy Settings
    resume_privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='private')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_profile_completion_percentage(self):
        fields = [
            self.phone_number, self.address, self.bio, self.job_title,
            self.company, self.industry, self.linkedin, self.github,
            self.portfolio, self.preferred_job_type, self.preferred_location,
            self.expected_salary
        ]
        filled_fields = sum(1 for field in fields if field)
        return int((filled_fields / len(fields)) * 100)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.accounts_profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance) 