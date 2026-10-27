from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime

from apps.appointments.models import Appointment, StatusAppointment
from apps.clients.models import Client
from apps.employees.models import Employee
from apps.services.models import Service

from apps.appointments.scheduling import find_conflicting_appointments
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

    
    def test_overlapping_appointment_is_conflict(self):
        new_start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))

        new_end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=new_start_base,
            end=new_end_base)
        
        self.assertIn(self.appointment, result)

    def test_scheduling_begins_at_the_limit_interval(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 40))

        end_base = timezone.make_aware(datetime(2026, 10, 25, 15, 10))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertNotIn(self.appointment, result)

    def test_scheduling_begins_within_the_interval(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 35))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 15, 5))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertIn(self.appointment, result)

    def test_end_of_the_appointment_within_the_safety_interval(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 13, 20))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 13, 55))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertIn(self.appointment, result)

    def test_ends_exactly_ten_minutes_before_the_next_appointment(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 13, 20))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 13, 50))      

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertNotIn(self.appointment, result)

    def test_appointment_of_another_employee_is_not_conflict(self):
        new_employee = Employee.objects.create(name="Pedro", email="pedro@gmail.com")

        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45))

        result = find_conflicting_appointments(
            employee=new_employee,
            start=start_base,
            end=end_base
        )

        self.assertNotIn(self.appointment, result)

    def test_cancelled_appointment_is_not_conflict(self):
        self.appointment.status = StatusAppointment.CANCELADO
        self.appointment.save(update_fields=['status'])

        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45))          

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base         
        )

        self.assertNotIn(self.appointment, result)

    def test_completed_appointment_is_not_conflict(self):
        self.appointment.status = StatusAppointment.CONCLUIDO
        self.appointment.save(update_fields=['status'])

        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45))          

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base          
        )

        self.assertNotIn(self.appointment, result)

    def test_appointment_is_conflict_without_exclude_appointment(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45)) 

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertIn(self.appointment, result)

    def test_appointment_is_ignored_with_exclude_appointment(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base,
            exclude_appointment=self.appointment
        ) 

        self.assertNotIn(self.appointment, result)     

    def test_returns_all_conflicting_appointments(self):
        client = Client.objects.create(name="Paulo", email="paulo@teste.com")
        service = Service.objects.create(name="Barba", duration=timedelta(minutes=30), price=10)

        second_appointment = Appointment.objects.create(
            client=client,
            employee=self.employee_base,
            start_time = timezone.make_aware(datetime(2026, 10, 25, 14, 40))
        )

        second_appointment.services.add(service)
        second_appointment.refresh_from_db()

        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertIn(self.appointment, result)
        self.assertIn(second_appointment, result)
        self.assertEqual(len(result), 2)

    def test_appointment_without_service_is_treated_as_zero_duration(self):
        appointment = Appointment.objects.create(
            client=self.client_base,
            employee=self.employee_base,
            start_time=timezone.make_aware(datetime(2026, 10, 25, 16, 0)),
            status=StatusAppointment.AGENDADO
        )

        start_base = timezone.make_aware(datetime(2026, 10, 25, 16, 5))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 16, 35))
        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertEqual(result, [appointment])
class AppointmentStrTestCase(TestCase):
    def setUp(self):
        self.client_base = Client.objects.create(name="Ana", email="ana@gmail.com")
        self.employee_base = Employee.objects.create(name="João", email="joao@gmail.com")
        self.service_base = Service.objects.create(name="Degradê", duration=timedelta(minutes=30), price=20)

    def test_str_displays_local_time_with_service(self):
        appointment = Appointment.objects.create(
            client=self.client_base,
            employee=self.employee_base,
            start_time=timezone.make_aware(datetime(2026, 10, 25, 14, 0))
        )

        appointment.services.add(self.service_base)
        appointment.refresh_from_db()

        self.assertEqual(
            str(appointment),
            "Ana | João | 25/10/2026 14:00 às 14:30"
        )

    def test_str_displays_notice_without_services(self):
        appointment = Appointment.objects.create(
            client=self.client_base,
            employee=self.employee_base,
            start_time=timezone.make_aware(datetime(2026, 10, 25, 14, 0))
        )

        appointment.refresh_from_db()

        self.assertEqual(
            str(appointment),
            "Ana | João | 25/10/2026 14:00 | Sem serviços"
        )