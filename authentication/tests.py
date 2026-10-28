from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User


class AuthenticationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_payload = {
            'name': 'Dr. Alice Carter',
            'email': 'alice.carter@hospital.com',
            'password': 'SecurePassword123!',
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertEqual(response.data['user']['email'], 'alice.carter@hospital.com')
        self.assertTrue(User.objects.filter(email='alice.carter@hospital.com').exists())

    def test_register_duplicate_email_fails(self):
        self.client.post(self.register_url, self.valid_payload, format='json')
        # Attempt registering same email again
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_register_short_password_fails(self):
        invalid_payload = {
            'name': 'Bob Tester',
            'email': 'bob@tester.com',
            'password': 'short',  # Less than 8 characters
        }
        response = self.client.post(self.register_url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success(self):
        # Register user first
        User.objects.create_user(
            email='alice.carter@hospital.com',
            name='Dr. Alice Carter',
            password='SecurePassword123!'
        )

        login_payload = {
            'email': 'alice.carter@hospital.com',
            'password': 'SecurePassword123!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_login_invalid_password_fails(self):
        User.objects.create_user(
            email='alice.carter@hospital.com',
            name='Dr. Alice Carter',
            password='SecurePassword123!'
        )
        login_payload = {
            'email': 'alice.carter@hospital.com',
            'password': 'WrongPassword!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_login_non_existent_email_fails(self):
        login_payload = {
            'email': 'nobody@hospital.com',
            'password': 'SomePassword123!',
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
