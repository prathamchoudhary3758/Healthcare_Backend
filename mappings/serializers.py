from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor
from patients.serializers import PatientSerializer
from doctors.serializers import DoctorSerializer


class PatientDoctorMappingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Patient-Doctor mapping.
    Supports either `patient`/`doctor` PrimaryKeyRelatedFields or integer IDs.
    """
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        help_text="ID of the patient"
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        help_text="ID of the doctor"
    )

    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'notes', 'assigned_at']
        read_only_fields = ['id', 'assigned_at']

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                f"Doctor '{doctor.name}' is already assigned to Patient '{patient.name}'."
            )
        return attrs


class PatientDoctorMappingReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading Patient-Doctor mapping records with full nested details.
    """
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = PatientDoctorMapping
        fields = [
            'id',
            'patient',
            'doctor',
            'notes',
            'assigned_at',
            'created_by',
            'created_by_name',
        ]
        read_only_fields = ['id', 'assigned_at', 'created_by', 'created_by_name']


class AssignedDoctorSerializer(serializers.Serializer):
    """
    Serializer representing doctor information assigned to a patient.
    """
    mapping_id = serializers.IntegerField(source='id')
    assigned_at = serializers.DateTimeField()
    notes = serializers.CharField(allow_blank=True, allow_null=True)
    doctor = DoctorSerializer()
