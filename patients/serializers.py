import re
from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient records.
    Automatically assigns `created_by` to the authenticated user on creation.
    """
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    created_by_email = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'contact_number',
            'email',
            'address',
            'medical_history',
            'created_by',
            'created_by_name',
            'created_by_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_by_email', 'created_at', 'updated_at']

    def validate_name(self, value):
        trimmed = value.strip()
        if len(trimmed) < 2:
            raise serializers.ValidationError("Patient name must be at least 2 characters long.")
        return trimmed

    def validate_contact_number(self, value):
        cleaned = value.strip()
        # Accept phone numbers with digits, optional leading +, spaces, dashes, parentheses
        if not re.match(r'^\+?[0-9\s\-\(\)]{7,20}$', cleaned):
            raise serializers.ValidationError("Please provide a valid contact phone number (7 to 20 digits).")
        return cleaned

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value
