from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Doctor
from .serializers import DoctorSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve all doctors",
        description="Returns a complete list of all registered doctors."
    ),
    create=extend_schema(
        summary="Add a new doctor",
        description="Registers a new doctor in the healthcare system (Authenticated users only)."
    ),
    retrieve=extend_schema(
        summary="Get details of a specific doctor",
        description="Retrieves the full profile of a specific doctor by ID."
    ),
    update=extend_schema(
        summary="Update doctor details",
        description="Updates all profile details of an existing doctor."
    ),
    partial_update=extend_schema(
        summary="Partially update doctor details",
        description="Updates specific fields of an existing doctor."
    ),
    destroy=extend_schema(
        summary="Delete a doctor record",
        description="Removes a doctor record from the system."
    )
)
class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor records:
    - POST /api/doctors/ : Add a new doctor (Authenticated users only)
    - GET /api/doctors/ : Retrieve all doctors
    - GET /api/doctors/<id>/ : Get details of a specific doctor
    - PUT /api/doctors/<id>/ : Update doctor details
    - DELETE /api/doctors/<id>/ : Delete a doctor record
    """
    queryset = Doctor.objects.all().order_by('name')
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        doctor_name = instance.name
        doctor_id = instance.id
        self.perform_destroy(instance)
        return Response(
            {
                "success": True,
                "message": f"Doctor '{doctor_name}' (ID: {doctor_id}) was deleted successfully."
            },
            status=status.HTTP_200_OK
        )
