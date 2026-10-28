"""
URL configuration for healthcare_backend project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Healthcare Backend API Root Information
    """
    return Response({
        "project": "Healthcare Management Backend API",
        "version": "1.0.0",
        "status": "online",
        "documentation": {
            "swagger_ui": request.build_absolute_uri('/api/docs/'),
            "redoc_ui": request.build_absolute_uri('/api/redoc/'),
            "openapi_schema": request.build_absolute_uri('/api/schema/'),
        },
        "endpoints": {
            "authentication": {
                "register": request.build_absolute_uri('/api/auth/register/'),
                "login": request.build_absolute_uri('/api/auth/login/'),
                "token_refresh": request.build_absolute_uri('/api/auth/token/refresh/'),
                "profile": request.build_absolute_uri('/api/auth/profile/'),
            },
            "patients": request.build_absolute_uri('/api/patients/'),
            "doctors": request.build_absolute_uri('/api/doctors/'),
            "mappings": request.build_absolute_uri('/api/mappings/'),
        }
    })


urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),

    # Root API Overview
    path('', api_root, name='root'),
    path('api/', api_root, name='api_root'),

    # OpenAPI 3 / Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Application APIs
    path('api/auth/', include('authentication.urls')),
    path('api/patients/', include('patients.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/mappings/', include('mappings.urls')),
]
