"""
Custom exception handlers for the storage app
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    and logs exceptions appropriately.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Convert Django ValidationError to DRF ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            response_data = exc.message_dict
        elif hasattr(exc, 'messages'):
            response_data = {'detail': exc.messages}
        else:
            response_data = {'detail': str(exc)}
        
        # Create a DRF ValidationError and get its response
        drf_exc = ValidationError(response_data)
        response = exception_handler(drf_exc, context)

    # Log the exception
    if response is not None:
        # Get request info for logging
        request = context.get('request')
        if request:
            logger.error(
                f"API Error: {exc.__class__.__name__} - "
                f"Path: {request.path} - "
                f"Method: {request.method} - "
                f"User: {request.user} - "
                f"Status: {response.status_code}"
            )
    else:
        # Unhandled exception
        logger.exception(
            f"Unhandled exception: {exc.__class__.__name__} - {str(exc)}"
        )

    return response
