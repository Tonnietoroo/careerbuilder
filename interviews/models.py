from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel
from django.utils.timezone import make_aware
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Industries"

class InterviewQuestion(models.Model):
    QUESTION_TYPES = [
        ('general', 'General'),
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral')
    ]
    
    question = models.TextField()
    answer = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question[:100]

class InterviewPrep(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_preps')
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    interview_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    questions = models.ManyToManyField(InterviewQuestion, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Interview Prep for {self.company_name}"

    class Meta:
        ordering = ['-interview_date']