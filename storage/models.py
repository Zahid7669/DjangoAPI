from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class Organization(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate organization data"""
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Organization name cannot be empty.'})


class User(AbstractUser):
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name='users')

    def __str__(self):
        return self.username


class UploadedFile(models.Model):
    owner = models.ForeignKey('storage.User', on_delete=models.CASCADE, related_name='uploaded_files')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=512)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Validate uploaded file data"""
        if not self.owner:
            raise ValidationError({'owner': 'File must have an owner.'})
        
        if not self.organization:
            raise ValidationError({'organization': 'File must belong to an organization.'})
        
        if not self.file:
            raise ValidationError({'file': 'No file attached.'})
        
        if not self.original_name or not self.original_name.strip():
            raise ValidationError({'original_name': 'Original filename cannot be empty.'})

    def save(self, *args, **kwargs):
        # Auto-assign organization from owner if not set
        if not self.organization and self.owner and self.owner.organization:
            self.organization = self.owner.organization
        
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_name} ({self.id})"


class Download(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey('storage.User', on_delete=models.CASCADE, related_name='downloads')
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Validate download record"""
        if not self.file:
            raise ValidationError({'file': 'Download must reference a file.'})
        
        if not self.user:
            raise ValidationError({'user': 'Download must reference a user.'})

    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} -> {self.file} at {self.timestamp}"
