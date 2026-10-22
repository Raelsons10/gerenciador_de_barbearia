from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime

from apps.appointments.models import Appointment
from apps.clients.models import Client
from apps.employees.models import Employee
from apps.services.models import Service
# Create your tests here.
class AppointmentOverlapTestCase(TestCase):
    def setUp(self):

        self.client_base = Client.objects.create(name="Ana", email="ana@teste.com")
        self.employee_base = Employee.objects.create(name="João", email="Joao@teste.com")
        self.service_base = Service.objects.create(name="Degradê", duration=timedelta(minutes=30), price=20)

        self.appointment = Appointment.objects.create(
            client=self.client_base,
            employee=self.employee_base,
            start_time=timezone.make_aware(datetime(2026, 10, 25, 14, 0))
        )

        self.appointment.services.add(self.service_base)

        self.appointment.refresh_from_db()

    def test_end_time(self):
        expected_end_time = timezone.make_aware(datetime(2026, 10, 25, 14, 30))

        self.assertEqual(self.appointment.end_time, expected_end_time)
