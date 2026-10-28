from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Patient(models.Model):
    """
    Patient model to store demographic and medical details.
    Linked to the user who created the patient record.
    """
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    name = models.CharField(max_length=255, help_text="Patient's full name")
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        help_text="Patient's age in years (0-150)"
    )
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, help_text="Gender identity")
    contact_number = models.CharField(max_length=20, help_text="Contact telephone/mobile number")
    email = models.EmailField(blank=True, null=True, help_text="Patient email (optional)")
    address = models.TextField(blank=True, null=True, help_text="Residential address (optional)")
    medical_history = models.TextField(blank=True, null=True, help_text="Summary of previous medical conditions/history (optional)")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',
        help_text="User who registered/created this patient record"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"{self.name} (Age: {self.age}, {self.gender})"
