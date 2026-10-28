from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .models import PatientDoctorMapping
from .serializers import (
    PatientDoctorMappingCreateSerializer,
    PatientDoctorMappingReadSerializer,
)
from patients.models import Patient
from doctors.models import Doctor


class MappingListCreateView(APIView):
    """
    POST /api/mappings/ - Assign a doctor to a patient (Authenticated users only)
    GET /api/mappings/ - Retrieve all patient-doctor mappings
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Retrieve all patient-doctor mappings",
        description="Returns a list of all active assignments between patients and doctors. Optional filter: ?patient_id= or ?doctor_id=",
        parameters=[
            OpenApiParameter(name='patient_id', description='Filter by Patient ID', required=False, type=int),
            OpenApiParameter(name='doctor_id', description='Filter by Doctor ID', required=False, type=int),
        ],
        responses={200: PatientDoctorMappingReadSerializer(many=True)}
    )
    def get(self, request):
        queryset = PatientDoctorMapping.objects.all().select_related('patient', 'doctor', 'created_by')

        patient_id = request.query_params.get('patient_id')
        doctor_id = request.query_params.get('doctor_id')

        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        serializer = PatientDoctorMappingReadSerializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "count": queryset.count(),
                "mappings": serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Assign a doctor to a patient",
        description="Creates a new association between a patient and a doctor.",
        request=PatientDoctorMappingCreateSerializer,
        responses={
            201: PatientDoctorMappingReadSerializer,
            400: OpenApiResponse(description="Validation error or duplicate assignment")
        }
    )
    def post(self, request):
        serializer = PatientDoctorMappingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mapping = serializer.save(created_by=request.user)

        # Return full details of created mapping
        read_serializer = PatientDoctorMappingReadSerializer(mapping)
        return Response(
            {
                "success": True,
                "message": f"Doctor '{mapping.doctor.name}' successfully assigned to patient '{mapping.patient.name}'.",
                "mapping": read_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class MappingDetailView(APIView):
    """
    Handles:
    - GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient.
    - DELETE /api/mappings/<id>/ - Remove a doctor from a patient by mapping ID.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get all doctors assigned to a specific patient",
        description="Retrieves list of all doctors assigned to the specified patient ID.",
        responses={
            200: OpenApiResponse(description="List of assigned doctors"),
            404: OpenApiResponse(description="Patient not found")
        }
    )
    def get(self, request, identifier):
        """
        Identifier here represents <patient_id> according to specification:
        GET /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient.
        """
        patient = Patient.objects.filter(id=identifier).first()
        if not patient:
            # Check if identifier might be a mapping id just in case
            mapping = PatientDoctorMapping.objects.filter(id=identifier).select_related('patient', 'doctor').first()
            if mapping:
                read_serializer = PatientDoctorMappingReadSerializer(mapping)
                return Response(
                    {
                        "success": True,
                        "mapping": read_serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {
                    "success": False,
                    "error": f"Patient with ID {identifier} not found.",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')

        doctors_data = [
            {
                "mapping_id": m.id,
                "assigned_at": m.assigned_at,
                "notes": m.notes,
                "doctor": {
                    "id": m.doctor.id,
                    "name": m.doctor.name,
                    "specialization": m.doctor.specialization,
                    "contact_number": m.doctor.contact_number,
                    "email": m.doctor.email,
                    "years_of_experience": m.doctor.years_of_experience,
                    "hospital_affiliation": m.doctor.hospital_affiliation
                }
            }
            for m in mappings
        ]

        return Response(
            {
                "success": True,
                "patient": {
                    "id": patient.id,
                    "name": patient.name,
                    "age": patient.age,
                    "gender": patient.gender,
                    "contact_number": patient.contact_number,
                },
                "total_doctors": len(doctors_data),
                "doctors": doctors_data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Remove a doctor from a patient",
        description="Deletes the mapping between doctor and patient using the mapping ID.",
        responses={
            200: OpenApiResponse(description="Doctor removed from patient successfully"),
            404: OpenApiResponse(description="Mapping record not found")
        }
    )
    def delete(self, request, identifier):
        """
        Identifier here represents mapping <id> according to specification:
        DELETE /api/mappings/<id>/ - Remove a doctor from a patient.
        """
        mapping = PatientDoctorMapping.objects.filter(id=identifier).first()
        if not mapping:
            return Response(
                {
                    "success": False,
                    "error": f"Patient-Doctor mapping with ID {identifier} not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        patient_name = mapping.patient.name
        doctor_name = mapping.doctor.name
        mapping_id = mapping.id
        mapping.delete()

        return Response(
            {
                "success": True,
                "message": f"Successfully removed Dr. '{doctor_name}' from patient '{patient_name}' (Mapping ID: {mapping_id})."
            },
            status=status.HTTP_200_OK
        )
