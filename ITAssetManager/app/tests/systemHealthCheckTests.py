from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Equipment

class SystemHealthCheckTests(TestCase):
    def setUp(self):
        # Create superuser for testing
        self.superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='password')
        self.client.login(username='admin', password='password')

        # Create initial equipment
        self.equipment_low_stock = Equipment.objects.create(
            name='Low Stock Equipment',
            stock=5,  # Below the threshold
            usage_status='free',
            condition_status='new',
            serial_number='LOWSTOCK123'
        )
        self.equipment_in_maintenance = Equipment.objects.create(
            name='Maintenance Equipment',
            stock=20,
            usage_status='maintenance',
            condition_status='good',
            serial_number='MAINT123'
        )
        self.equipment_in_repair = Equipment.objects.create(
            name='Repair Equipment',
            stock=30,
            usage_status='in_repair',
            condition_status='fair',
            serial_number='REPAIR123'
        )

    def test_system_health_check_view(self):
        response = self.client.get(reverse('system_health_check'))
        self.assertEqual(response.status_code, 200)

        low_stock_count = response.context['low_stock_count']
        maintenance_count = response.context['maintenance_count']
        repair_count = response.context['repair_count']
        system_health = response.context['system_health']

        # Validate the counts
        self.assertEqual(low_stock_count, 1) 
        self.assertEqual(maintenance_count, 1)  
        self.assertEqual(repair_count, 1) 

        # Validate system health percentage
        total_equipment = Equipment.objects.count()
        expected_health = ((total_equipment - (low_stock_count + maintenance_count + repair_count)) / total_equipment) * 100
        self.assertAlmostEqual(system_health, expected_health)
