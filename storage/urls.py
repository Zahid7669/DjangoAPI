from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UploadedFileViewSet, OrganizationViewSet, DownloadViewSet

router = DefaultRouter()
router.register(r'files', UploadedFileViewSet, basename='file')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'downloads', DownloadViewSet, basename='download')

urlpatterns = [
    path('', include(router.urls)),
]
