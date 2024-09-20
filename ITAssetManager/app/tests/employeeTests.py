from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Employee, Equipment

class EmployeeViewTests(TestCase):
    def setUp(self):
        # Create superuser and regular user for testing
        self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.client.login(username='admin', password='password')

        # Create initial equipment and employee
        self.equipment = Equipment.objects.create(
            name='Test Equipment', 
            stock=10, 
            usage_status='free',
            condition_status='new',
            serial_number='TEST123'
        )
        self.employee = Employee.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            position='intern',
            hire_date='2024-09-19'
        )
        self.employee.equipment.add(self.equipment)

    def test_employee_list_view(self):
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_employee_detail_view(self):
        response = self.client.get(reverse('employee_detail', kwargs={'pk': self.employee.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_employee_create_view(self):
        response = self.client.post(reverse('employee_create'), {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone_number': '1234567890',
            'position': 'manager',
            'hire_date': '2024-09-19'
        })

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Verify the employee was created
        self.assertTrue(Employee.objects.filter(email='jane.smith@example.com').exists())

    def test_employee_update_view(self):
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Doe',
            'email': 'updated.doe@example.com',
            'phone_number': '0987654321',
            'position': 'contractor',
            'hire_date': '2024-09-20'
        }

        response = self.client.post(reverse('employee_update', kwargs={'pk': self.employee.pk}), update_data)
        
        self.assertEqual(response.status_code, 302)

        # Refresh the employee instance and verify the changes
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.first_name, 'Updated')
        self.assertEqual(self.employee.last_name, 'Doe')
        self.assertEqual(self.employee.email, 'updated.doe@example.com')
        self.assertEqual(self.employee.position, 'contractor')
        self.assertEqual(self.employee.phone_number, '0987654321')

    def test_employee_delete_view(self):
        response = self.client.post(reverse('employee_delete', kwargs={'pk': self.employee.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Employee.objects.filter(pk=self.employee.pk).exists())
