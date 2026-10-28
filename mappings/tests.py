from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping


class MappingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='nurse@hospital.com',
            name='Nurse Nancy',
            password='Password123!'
        )
        self.client.force_authenticate(user=self.user)

        self.patient = Patient.objects.create(
            name='Sarah Connor',
            age=33,
            gender='Female',
            contact_number='+1-555-4321',
            created_by=self.user
        )

        self.doctor1 = Doctor.objects.create(
            name='Leonard McCoy',
            specialization='Chief Medical Officer',
            contact_number='+1-555-8888',
            email='mccoy@enterprise.starfleet',
            years_of_experience=15,
        )

        self.doctor2 = Doctor.objects.create(
            name='Beverly Crusher',
            specialization='General Medicine & Exobiology',
            contact_number='+1-555-9999',
            email='crusher@enterprise.starfleet',
            years_of_experience=18,
        )

    def test_assign_doctor_to_patient(self):
        payload = {
            'patient': self.patient.id,
            'doctor': self.doctor1.id,
            'notes': 'Primary physician assignment.',
        }
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(PatientDoctorMapping.objects.count(), 1)
        mapping = PatientDoctorMapping.objects.first()
        self.assertEqual(mapping.patient, self.patient)
        self.assertEqual(mapping.doctor, self.doctor1)

    def test_assign_duplicate_doctor_to_patient_fails(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            created_by=self.user
        )
        payload = {
            'patient': self.patient.id,
            'doctor': self.doctor1.id,
        }
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_retrieve_all_mappings(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            created_by=self.user
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor2,
            created_by=self.user
        )
        response = self.client.get('/api/mappings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_get_all_doctors_assigned_to_specific_patient(self):
        # Assign both doctor1 and doctor2 to patient
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            notes='Cardiology consult',
            created_by=self.user
        )
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor2,
            notes='Routine check',
            created_by=self.user
        )

        response = self.client.get(f'/api/mappings/{self.patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['total_doctors'], 2)
        doctor_names = [d['doctor']['name'] for d in response.data['doctors']]
        self.assertIn('Leonard McCoy', doctor_names)
        self.assertIn('Beverly Crusher', doctor_names)

    def test_remove_doctor_from_patient(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            created_by=self.user
        )
        mapping_id = mapping.id
        delete_url = f'/api/mappings/{mapping_id}/'
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping_id).exists())
