from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class Industry(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

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
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=True, blank=True)  # Changed from JobCategory to Industry
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
    questions = models.ManyToManyField(InterviewQuestion)
    
    def __str__(self):
        return f"{self.user.username}'s Interview Prep for {self.company_name}" 