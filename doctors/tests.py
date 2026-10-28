from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import User
from .models import Doctor


class DoctorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@hospital.com',
            name='Hospital Admin',
            password='AdminPassword123!'
        )
        self.list_create_url = '/api/doctors/'
        self.client.force_authenticate(user=self.user)

    def test_unauthenticated_access_denied(self):
        unauth_client = APIClient()
        response = unauth_client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_success(self):
        payload = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine & Nephrology',
            'contact_number': '+1-555-0100',
            'email': 'house@princetonplainsboro.org',
            'years_of_experience': 20,
            'hospital_affiliation': 'Princeton-Plainsboro Teaching Hospital',
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Gregory House')
        self.assertEqual(response.data['specialization'], 'Diagnostic Medicine & Nephrology')
        self.assertTrue(Doctor.objects.filter(email='house@princetonplainsboro.org').exists())

    def test_create_doctor_duplicate_email_fails(self):
        Doctor.objects.create(
            name='James Wilson',
            specialization='Oncology',
            contact_number='555-0101',
            email='wilson@ppth.org',
            years_of_experience=15,
        )
        payload = {
            'name': 'Another Doctor',
            'specialization': 'General Medicine',
            'contact_number': '555-0102',
            'email': 'wilson@ppth.org',  # Duplicate email
            'years_of_experience': 5,
        }
        response = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_doctors(self):
        Doctor.objects.create(
            name='Lisa Cuddy',
            specialization='Endocrinology',
            contact_number='555-0103',
            email='cuddy@ppth.org',
            years_of_experience=18,
        )
        Doctor.objects.create(
            name='Allison Cameron',
            specialization='Immunology',
            contact_number='555-0104',
            email='cameron@ppth.org',
            years_of_experience=7,
        )
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertEqual(len(results), 2)

    def test_retrieve_doctor_details(self):
        doctor = Doctor.objects.create(
            name='Robert Chase',
            specialization='Intensive Care & Surgery',
            contact_number='555-0105',
            email='chase@ppth.org',
            years_of_experience=10,
        )
        detail_url = f'/api/doctors/{doctor.id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Robert Chase')
        self.assertEqual(response.data['specialization'], 'Intensive Care & Surgery')

    def test_update_doctor_details(self):
        doctor = Doctor.objects.create(
            name='Eric Foreman',
            specialization='Neurology',
            contact_number='555-0106',
            email='foreman@ppth.org',
            years_of_experience=8,
        )
        update_url = f'/api/doctors/{doctor.id}/'
        updated_payload = {
            'name': 'Eric Foreman',
            'specialization': 'Pediatric Neurology',
            'contact_number': '555-0106',
            'email': 'foreman@ppth.org',
            'years_of_experience': 10,
            'hospital_affiliation': 'Princeton-Plainsboro',
        }
        response = self.client.put(update_url, updated_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doctor.refresh_from_db()
        self.assertEqual(doctor.specialization, 'Pediatric Neurology')
        self.assertEqual(doctor.years_of_experience, 10)

    def test_delete_doctor(self):
        doctor = Doctor.objects.create(
            name='Chris Taub',
            specialization='Plastic Surgery',
            contact_number='555-0107',
            email='taub@ppth.org',
            years_of_experience=16,
        )
        delete_url = f'/api/doctors/{doctor.id}/'
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())
