from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for standardized JSON error responses across the API.
    Format:
    {
        "success": False,
        "error": "Error summary",
        "details": ...
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_message = "Validation or request error"

        if isinstance(response.data, dict):
            if "detail" in response.data:
                error_message = str(response.data["detail"])
            elif response.data:
                first_key = next(iter(response.data))
                first_val = response.data[first_key]
                if isinstance(first_val, list) and len(first_val) > 0:
                    error_message = f"{first_key}: {first_val[0]}"
                else:
                    error_message = f"{first_key}: {first_val}"

        response.data = {
            "success": False,
            "status_code": response.status_code,
            "error": error_message,
            "details": response.data,
        }
    else:
        logger.error(f"Unhandled Exception: {exc}", exc_info=True)
        response = Response(
            {
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": "Internal server error occurred. Please contact support.",
                "details": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
