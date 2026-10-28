from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor


class PatientDoctorMapping(models.Model):
    """
    Mapping model linking a Patient to an assigned Doctor.
    Ensures a doctor cannot be assigned multiple times to the same patient.
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        help_text="The patient receiving care"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        help_text="The assigned doctor"
    )
    assigned_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when assignment was made")
    notes = models.TextField(blank=True, null=True, help_text="Clinical or administrative notes regarding this assignment")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_mappings',
        help_text="User who created this mapping"
    )

    class Meta:
        ordering = ['-assigned_at']
        verbose_name = 'Patient-Doctor Mapping'
        verbose_name_plural = 'Patient-Doctor Mappings'
        constraints = [
            models.UniqueConstraint(
                fields=['patient', 'doctor'],
                name='unique_patient_doctor_assignment'
            )
        ]

    def __str__(self):
        return f"Patient '{self.patient.name}' -> Dr. '{self.doctor.name}'"
