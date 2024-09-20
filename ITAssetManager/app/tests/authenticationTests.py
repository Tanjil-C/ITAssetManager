from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_successful_login(self):
        """Test if login works with valid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertRedirects(response, reverse('home'))  # Redirects to home page

    def test_failed_login(self):
        """Test login with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertContains(response, 'Invalid credentials')  # Error message shown

    def test_logout(self):
        """Test logout functionality."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))  # Redirects to login after logout

    def test_jwt_token_generation(self):
        """Test JWT token generation on login."""
        response = self.client.post(reverse('jwt_login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())  # Check if access token is returned
        self.assertIn('refresh', response.json())  # Check if refresh token is returned
