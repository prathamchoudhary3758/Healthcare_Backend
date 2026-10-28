from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'gender', 'contact_number', 'created_by', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'contact_number', 'email', 'medical_history')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
