from django.contrib import admin
from .models import Organization, User, UploadedFile, Download


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'organization')


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_name', 'owner', 'organization', 'uploaded_at')


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'user', 'timestamp')
