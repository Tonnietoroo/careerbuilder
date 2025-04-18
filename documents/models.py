from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel
from django.utils import timezone
from django.utils.timezone import now

class CVTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="No description available")
    preview_image = models.ImageField(upload_to='cv_templates/previews/', null=True, blank=True)
    html_template = models.FileField(upload_to='cv_templates/html/', null=True, blank=True)
    css_template = models.FileField(upload_to='cv_templates/css/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class CV(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(CVTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    content = models.JSONField()
    generated_file = models.FileField(upload_to='generated_cvs/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s CV - {self.title}"

    class Meta:
        verbose_name = "CV"
        verbose_name_plural = "CVs"

class CoverLetter(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, null=True, blank=True)
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_address = models.TextField(blank=True)
    content = models.TextField()
    
    def __str__(self):
        return f"Cover Letter for {self.company_name} - {self.job_title}"

class DocumentFolder(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s folder - {self.name}"
    
    class Meta:
        unique_together = ['user', 'name', 'parent']

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('cv', 'CV'),
        ('cover_letter', 'Cover Letter'),
        ('other', 'Other')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=now) 
    content = models.JSONField(null=True, blank=True)  # For storing extracted content
    is_parsed = models.BooleanField(default=False)  # Flag to track if content has been extracted
    
    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.get_document_type_display()}"

class DocumentShare(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_documents')
    can_edit = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['document', 'shared_with']
