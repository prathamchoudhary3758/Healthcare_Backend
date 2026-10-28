import re
from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor records.
    """
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'contact_number',
            'email',
            'years_of_experience',
            'hospital_affiliation',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at', 'updated_at']

    def validate_name(self, value):
        trimmed = value.strip()
        if len(trimmed) < 2:
            raise serializers.ValidationError("Doctor name must be at least 2 characters long.")
        return trimmed

    def validate_specialization(self, value):
        trimmed = value.strip()
        if len(trimmed) < 2:
            raise serializers.ValidationError("Specialization must be at least 2 characters long.")
        return trimmed

    def validate_email(self, value):
        normalized = value.strip().lower()
        # Ensure email uniqueness during creation and update
        qs = Doctor.objects.filter(email=normalized)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("A doctor with this email address is already registered.")
        return normalized

    def validate_contact_number(self, value):
        cleaned = value.strip()
        if not re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', cleaned):
            raise serializers.ValidationError("Please provide a valid contact phone number (7 to 20 digits).")
        return cleaned

    def validate_years_of_experience(self, value):
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        if value > 75:
            raise serializers.ValidationError("Years of experience must be realistic (0-75).")
        return value
