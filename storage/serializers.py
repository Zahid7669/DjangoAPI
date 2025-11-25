from rest_framework import serializers
from .models import UploadedFile, Download, Organization, User
from django.db.models import Count


class UploadedFileSerializer(serializers.ModelSerializer):
    download_count = serializers.IntegerField(read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UploadedFile
        fields = ['id', 'original_name', 'file', 'owner', 'organization', 'uploaded_at', 'download_count']
        read_only_fields = ['owner', 'organization', 'uploaded_at', 'download_count', 'original_name']


class OrganizationSerializer(serializers.ModelSerializer):
    total_downloads = serializers.IntegerField(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'total_downloads']


class DownloadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    file = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Download
        fields = ['id', 'file', 'user', 'timestamp']
