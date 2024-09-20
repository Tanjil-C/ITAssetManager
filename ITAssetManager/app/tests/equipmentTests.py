from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Equipment, Employee

class EquipmentTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.user = User.objects.create_user(username='user', email='user@example.com', password='password')
        self.client.login(username='admin', password='password')
        self.equipment = Equipment.objects.create(name='Test Equipment', stock=10, usage_status='free')

    def test_equipment_list_view(self):
        response = self.client.get(reverse('equipment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Equipment')

    def test_equipment_detail_view(self):
        response = self.client.get(reverse('equipment_detail', kwargs={'pk': self.equipment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Equipment')

    def test_equipment_create_view(self):
        # POST request to create new equipment
        response = self.client.post(reverse('equipment_create'), {
            'name': 'New Equipment',
            'description': 'A description of new equipment',
            'purchased_date': '2024-09-19',  
            'serial_number': 'NEW123',
            'condition_status': 'new',
            'usage_status': 'free',
            'stock': 10
        })

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Verify the equipment was created
        self.assertTrue(Equipment.objects.filter(name='New Equipment').exists())

    def test_equipment_update_view(self):
        # Prepare the update data
        update_data = {
            'name': 'Updated Equipment',
            'description': 'Updated description',
            'purchased_date': '2024-09-19', 
            'serial_number': 'UPD123',
            'condition_status': 'good',
            'usage_status': 'maintenance',
            'stock': 5
        }

        # Perform POST request to update the equipment
        response = self.client.post(reverse('equipment_update', kwargs={'pk': self.equipment.pk}), update_data)

        self.assertEqual(response.status_code, 302)

        # Refresh the equipment instance and verify the changes
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.name, 'Updated Equipment')
        self.assertEqual(self.equipment.serial_number, 'UPD123')
        self.assertEqual(self.equipment.condition_status, 'good')
        self.assertEqual(self.equipment.usage_status, 'maintenance')
        self.assertEqual(self.equipment.stock, 5)

    def test_equipment_delete_view(self):
        response = self.client.post(reverse('equipment_delete', kwargs={'pk': self.equipment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Equipment.objects.filter(pk=self.equipment.pk).exists())

    def test_assign_equipment_list_view(self):
        employee = Employee.objects.create(first_name='Test', last_name='Employee', email='employee@example.com')
        response = self.client.post(reverse('assign_equipment_list'), {
            'employee': employee.pk,
            'equipment': self.equipment.pk
        })
        self.assertEqual(response.status_code, 302)  
        employee.refresh_from_db()
        self.assertIn(self.equipment, employee.equipment.all())
