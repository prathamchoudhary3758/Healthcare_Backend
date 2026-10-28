from django.contrib import admin
from .models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'assigned_at', 'created_by')
    list_filter = ('assigned_at',)
    search_fields = ('patient__name', 'doctor__name', 'notes')
    ordering = ('-assigned_at',)
    readonly_fields = ('assigned_at',)
