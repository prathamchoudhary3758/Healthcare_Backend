from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'contact_number', 'email', 'years_of_experience', 'hospital_affiliation')
    list_filter = ('specialization', 'years_of_experience')
    search_fields = ('name', 'specialization', 'email', 'hospital_affiliation')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
