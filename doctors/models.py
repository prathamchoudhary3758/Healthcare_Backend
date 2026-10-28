from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Doctor(models.Model):
    """
    Doctor model to store doctor profile, specialization, and contact information.
    """
    name = models.CharField(max_length=255, help_text="Doctor's full name (e.g. Dr. Jane Smith)")
    specialization = models.CharField(max_length=255, help_text="Medical specialty (e.g. Cardiology, Neurology)")
    contact_number = models.CharField(max_length=20, help_text="Contact telephone/mobile number")
    email = models.EmailField(unique=True, help_text="Doctor's professional email address")
    years_of_experience = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of years in professional practice"
    )
    hospital_affiliation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Hospital or clinic affiliation"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors_added',
        help_text="User who added this doctor to the directory"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
