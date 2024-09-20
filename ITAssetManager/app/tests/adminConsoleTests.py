from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User

class AdminConsoleTests(TestCase):
    def setUp(self):
        # Create superuser for testing
        self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.user = User.objects.create_user(username='user', email='user@example.com', password='password')

        # Log in as superuser
        self.client.login(username='admin', password='password')

    def test_admin_console_access(self):
        response = self.client.get(reverse('admin_console'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin's Console")
        self.assertContains(response, self.superuser.username)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.superuser.email)
        self.assertContains(response, self.user.email)
        self.assertContains(response, 'Remove Admin')
        self.assertContains(response, 'Make Admin')

    def test_toggle_superuser_status_without_permission(self):
        # Create a regular user for this test
        regular_user = User.objects.create_user(username='regularuser', email='regularuser@example.com', password='password')

        # Log in as the regular user
        self.client.login(username='regularuser', password='password')
        
        # Try to access the toggle superuser status URL
        response = self.client.post(reverse('toggle_superuser_status', kwargs={'user_id': self.superuser.id}))
        self.assertEqual(response.status_code, 403)  

    def test_toggle_superuser_status_with_permission(self):
        regular_user = User.objects.create_user(username='regularuser', email='regularuser@example.com', password='password')

        self.client.login(username='admin', password='password')

        response = self.client.post(reverse('toggle_superuser_status', kwargs={'user_id': regular_user.id}))

        # Check that the status was updated
        self.assertEqual(response.status_code, 302)  # Redirect after status change
        updated_user = User.objects.get(id=regular_user.id)
        self.assertTrue(updated_user.is_superuser)
