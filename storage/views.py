from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import Count
from django.db import DatabaseError, IntegrityError
import logging

from .models import UploadedFile, Organization, Download
from .serializers import UploadedFileSerializer, OrganizationSerializer, DownloadSerializer

logger = logging.getLogger(__name__)


class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all().select_related('owner', 'organization')
    serializer_class = UploadedFileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']  # Exclude PUT and PATCH

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(download_count=Count('downloads'))
        return qs.order_by('-uploaded_at')  # Most recent first

    def perform_create(self, serializer):
        user = self.request.user
        
        # Validate user has an organization
        if not user.organization:
            logger.warning(f"User {user.username} attempted to upload file without organization")
            raise ValidationError({
                'organization': 'User must belong to an organization to upload files. Please contact an administrator.'
            })
        
        # Validate file was uploaded
        uploaded_file = self.request.FILES.get('file')
        if not uploaded_file:
            raise ValidationError({
                'file': 'No file was uploaded. Please select a file to upload.'
            })
        
        # Validate file size (10MB limit)
        max_file_size = 10 * 1024 * 1024  # 10 MB in bytes
        if uploaded_file.size > max_file_size:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            logger.warning(f"User {user.username} attempted to upload file {uploaded_file.name} ({file_size_mb:.2f}MB) exceeding limit")
            raise ValidationError({
                'file': f'File size ({file_size_mb:.2f} MB) exceeds the maximum allowed size of 10 MB.'
            })
        
        try:
            original_name = uploaded_file.name
            serializer.save(
                owner=user,
                organization=user.organization,
                original_name=original_name
            )
            logger.info(f"User {user.username} uploaded file: {original_name} ({uploaded_file.size} bytes)")
        except IntegrityError as e:
            logger.error(f"Database integrity error during file upload: {str(e)}")
            raise ValidationError({
                'detail': 'Failed to save file due to database constraint violation.'
            })
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            raise ValidationError({
                'detail': 'An unexpected error occurred while uploading the file.'
            })

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            obj = get_object_or_404(UploadedFile, pk=pk)
            
            # Record download
            try:
                Download.objects.create(file=obj, user=request.user)
                logger.info(f"User {request.user.username} downloaded file {obj.id}: {obj.original_name}")
            except DatabaseError as e:
                logger.error(f"Failed to record download for file {obj.id}: {str(e)}")
                # Continue with download even if recording fails
            
            # Attempt to open and serve the file
            try:
                file_handle = obj.file.open('rb')
                response = FileResponse(
                    file_handle,
                    as_attachment=True,
                    filename=obj.original_name
                )
                return response
            except FileNotFoundError:
                logger.error(f"File not found on disk for UploadedFile {obj.id}: {obj.file.name}")
                raise Http404("The requested file no longer exists on the server.")
            except PermissionError:
                logger.error(f"Permission denied accessing file {obj.id}: {obj.file.name}")
                raise ValidationError({
                    'detail': 'Permission denied: Unable to access the file.'
                })
            except IOError as e:
                logger.error(f"IO error reading file {obj.id}: {str(e)}")
                raise ValidationError({
                    'detail': 'Failed to read the file. The file may be corrupted.'
                })
                
        except Http404:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file download: {str(e)}")
            raise ValidationError({
                'detail': 'An unexpected error occurred while downloading the file.'
            })


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['name']  # Alphabetical order

    def get_queryset(self):
        try:
            qs = super().get_queryset()
            # total downloads = count of downloads via files
            qs = qs.annotate(total_downloads=Count('files__downloads'))
            return qs.order_by('name')  # Ensure ordering is applied
        except DatabaseError as e:
            logger.error(f"Database error fetching organizations: {str(e)}")
            raise ValidationError({
                'detail': 'Failed to retrieve organizations due to a database error.'
            })


class DownloadViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Download.objects.all().select_related('user', 'file')
    serializer_class = DownloadSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-timestamp']  # Newest downloads first

    def _validate_and_filter_by_id(self, queryset, param_name, filter_field, model_class, model_name):
        """Helper method to validate ID parameter and filter queryset"""
        param_value = self.request.query_params.get(param_name)
        if not param_value:
            return queryset
        
        try:
            param_id = int(param_value)
            # Check if the record exists
            if not model_class.objects.filter(id=param_id).exists():
                logger.warning(f"{model_name} with ID {param_id} does not exist")
                raise ValidationError({
                    param_name: f'{model_name} with ID {param_id} does not exist.'
                })
            return queryset.filter(**{filter_field: param_id})
        except ValueError:
            logger.warning(f"Invalid {param_name} parameter: {param_value}")
            raise ValidationError({
                param_name: f'Invalid {param_name} ID: "{param_value}". Must be a valid integer.'
            })

    def get_queryset(self):
        try:
            qs = super().get_queryset()
            
            # Validate and filter by user_id
            from .models import User
            qs = self._validate_and_filter_by_id(qs, 'user', 'user__id', User, 'User')
            
            # Validate and filter by file_id
            qs = self._validate_and_filter_by_id(qs, 'file', 'file__id', UploadedFile, 'File')
            
            return qs.order_by('-timestamp')
            
        except ValidationError:
            raise
        except DatabaseError as e:
            logger.error(f"Database error fetching downloads: {str(e)}")
            raise ValidationError({
                'detail': 'Failed to retrieve downloads due to a database error.'
            })
        except Exception as e:
            logger.error(f"Unexpected error fetching downloads: {str(e)}")
            raise ValidationError({
                'detail': 'An unexpected error occurred while retrieving downloads.'
            })
