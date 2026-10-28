from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from .models import Patient


class PatientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@hospital.com',
            name='User One',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            email='user2@hospital.com',
            name='User Two',
            password='Password123!'
        )

        self.list_create_url = '/api/patients/'

        # Authenticate as user1 by default
        self.client.force_authenticate(user=self.user1)

    def test_unauthenticated_access_denied(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient(self):
        payload = {
            'name': 'John Doe',
            'age': 45,
            'gender': 'Male',
            'contact_number': '+1-555-0199',
            'email': 'johndoe@example.com',
            'address': '123 Elm Street, Cityville',
            'medical_history': 'Hypertension diagnosed in 2020.',
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['created_by_email'], self.user1.email)
        self.assertEqual(Patient.objects.count(), 1)
        self.assertEqual(Patient.objects.first().created_by, self.user1)

    def test_list_patients_only_returns_created_by_user(self):
        # Create patient for user1
        p1 = Patient.objects.create(
            name='Patient User1',
            age=30,
            gender='Female',
            contact_number='1234567890',
            created_by=self.user1
        )
        # Create patient for user2
        p2 = Patient.objects.create(
            name='Patient User2',
            age=50,
            gender='Male',
            contact_number='0987654321',
            created_by=self.user2
        )

        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only user1's patient should be in results
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], p1.id)
        self.assertEqual(results[0]['name'], 'Patient User1')

    def test_retrieve_patient_details(self):
        patient = Patient.objects.create(
            name='Jane Smith',
            age=28,
            gender='Female',
            contact_number='555-432-1111',
            created_by=self.user1
        )
        detail_url = f'/api/patients/{patient.id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Jane Smith')
        self.assertEqual(response.data['age'], 28)

    def test_update_patient_details(self):
        patient = Patient.objects.create(
            name='Michael Brown',
            age=35,
            gender='Male',
            contact_number='555-123-4567',
            created_by=self.user1
        )
        update_url = f'/api/patients/{patient.id}/'
        updated_payload = {
            'name': 'Michael Brown Jr.',
            'age': 36,
            'gender': 'Male',
            'contact_number': '555-123-9999',
            'medical_history': 'Updated routine physical examination.',
        }
        response = self.client.put(update_url, updated_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.name, 'Michael Brown Jr.')
        self.assertEqual(patient.age, 36)
        self.assertEqual(patient.contact_number, '555-123-9999')

    def test_delete_patient(self):
        patient = Patient.objects.create(
            name='Sarah Connor',
            age=40,
            gender='Female',
            contact_number='555-987-6543',
            created_by=self.user1
        )
        delete_url = f'/api/patients/{patient.id}/'
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())

    def test_cannot_access_or_modify_other_user_patient(self):
        # Patient created by user2
        patient_user2 = Patient.objects.create(
            name='Confidential Patient',
            age=60,
            gender='Other',
            contact_number='555-000-1111',
            created_by=self.user2
        )
        # Attempt to access with user1
        detail_url = f'/api/patients/{patient_user2.id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
