from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel

class CVTemplate(models.Model):
    name = models.CharField(max_length=100)
    template_file = models.FileField(upload_to='cv_templates/')
    preview_image = models.ImageField(upload_to='cv_previews/')
    
    def __str__(self):
        return self.name

class CV(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(CVTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    content = models.JSONField()
    generated_file = models.FileField(upload_to='generated_cvs/', null=True)
    
    def __str__(self):
        return f"{self.user.username}'s CV - {self.title}"

class CoverLetter(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, null=True, blank=True)
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    company_address = models.TextField(blank=True)
    content = models.TextField()
    
    def __str__(self):
        return f"Cover Letter for {self.company_name} - {self.job_title}"

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class InterviewQuestion(models.Model):
    QUESTION_TYPES = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('general', 'General'),
    ]
    
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question = models.TextField()
    answer = models.TextField()
    
    def __str__(self):
        return f"{self.category.name} - {self.question_type}"

class InterviewPrep(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_interview_preps')
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    interview_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    questions = models.ManyToManyField(InterviewQuestion)
    
    def __str__(self):
        return f"{self.user.username}'s Interview Prep for {self.company_name}"

class DocumentFolder(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s folder - {self.name}"
    
    def get_breadcrumbs(self):
        """Return list of parent folders for navigation"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.append(current)
            current = current.parent
        return reversed(breadcrumbs)
    
    def get_document_count(self):
        """Return count of documents in this folder"""
        return self.document_set.count()
    
    def get_subfolder_count(self):
        """Return count of subfolders"""
        return DocumentFolder.objects.filter(parent=self).count()
    
    class Meta:
        unique_together = ['user', 'name', 'parent']

class DocumentShare(TimeStampedModel):
    document = models.ForeignKey('Document', on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_documents')
    can_edit = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['document', 'shared_with']

class Document(TimeStampedModel):
    DOCUMENT_TYPES = [
        ('cv', 'CV'),
        ('cover_letter', 'Cover Letter'),
        ('other', 'Other')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(DocumentFolder, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='user_documents/')
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_document_type_display()} - {self.title}"
    
    def get_file_size(self):
        """Return file size in a human-readable format"""
        size = self.file.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def get_file_extension(self):
        """Return the file extension"""
        return self.file.name.split('.')[-1].lower()
    
    def is_image(self):
        """Check if the file is an image"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        return self.get_file_extension() in image_extensions
    
    def get_preview_url(self):
        """Get preview URL based on file type"""
        if self.is_image():
            return self.file.url
        return None
    
    def share_with_user(self, user, can_edit=False):
        """Share document with another user"""
        return DocumentShare.objects.create(
            document=self,
            shared_with=user,
            can_edit=can_edit
        )
    
    def get_shared_users(self):
        """Get list of users this document is shared with"""
        return User.objects.filter(documentshare__document=self) 