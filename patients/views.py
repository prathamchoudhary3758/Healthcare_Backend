from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Patient
from .serializers import PatientSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve all patients created by the authenticated user",
        description="Returns a list of all patient records created by the currently authenticated user."
    ),
    create=extend_schema(
        summary="Add a new patient",
        description="Creates a new patient record and links it to the authenticated user."
    ),
    retrieve=extend_schema(
        summary="Get details of a specific patient",
        description="Retrieves full details of a specific patient created by the authenticated user."
    ),
    update=extend_schema(
        summary="Update patient details",
        description="Completely updates a patient's details."
    ),
    partial_update=extend_schema(
        summary="Partially update patient details",
        description="Updates specific fields of a patient record."
    ),
    destroy=extend_schema(
        summary="Delete a patient record",
        description="Deletes a patient record created by the authenticated user."
    )
)
class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patient records:
    - POST /api/patients/ : Add a new patient
    - GET /api/patients/ : Retrieve all patients created by the authenticated user
    - GET /api/patients/<id>/ : Get details of a specific patient
    - PUT /api/patients/<id>/ : Update patient details
    - DELETE /api/patients/<id>/ : Delete a patient record
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Authenticated users can only see patients they created
        user = self.request.user
        if not user.is_authenticated:
            return Patient.objects.none()
        
        # Staff users can optionally pass ?all=true to view all patients
        if user.is_staff and self.request.query_params.get('all') == 'true':
            return Patient.objects.all().order_by('-created_at')

        return Patient.objects.filter(created_by=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        patient_name = instance.name
        patient_id = instance.id
        self.perform_destroy(instance)
        return Response(
            {
                "success": True,
                "message": f"Patient '{patient_name}' (ID: {patient_id}) was deleted successfully."
            },
            status=status.HTTP_200_OK
        )
