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
    """
    Tests for find_conflicting_appointments.

    Every scenario is built around one existing appointment (set up below):
    14:00-14:30 for the same barber, which reserves the time up to 14:40
    once the 10-minute buffer is added.
    """
    def setUp(self):
        # Existing appointment: 14:00-14:30 (one 30-minute service).
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

    # 14:00 plus the 30-minute service must end at 14:30.
    def test_end_time(self):
        expected_end_time = timezone.make_aware(datetime(2026, 10, 25, 14, 30))

        self.assertEqual(self.appointment.end_time, expected_end_time)

    # 14:15-14:45 starts while the existing appointment is still running.
    def test_overlapping_appointment_is_conflict(self):
        new_start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))

        new_end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=new_start_base,
            end=new_end_base)
        
        self.assertIn(self.appointment, result)

    # 14:35 starts inside the buffer (14:30-14:40): conflict.
    def test_scheduling_begins_at_the_limit_interval(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 40))

        end_base = timezone.make_aware(datetime(2026, 10, 25, 15, 10))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertNotIn(self.appointment, result)

    # Boundary: 14:40 starts exactly when the buffer ends, so it is free.
    def test_scheduling_begins_within_the_interval(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 35))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 15, 5))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertIn(self.appointment, result)

    # 13:20-13:55: its own buffer runs until 14:05, past the 14:00 start: conflict.
    def test_end_of_the_appointment_within_the_safety_interval(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 13, 20))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 13, 55))

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertIn(self.appointment, result)

    # Boundary: 13:20-13:50: its buffer ends exactly at 14:00, so it is free.
    def test_ends_exactly_ten_minutes_before_the_next_appointment(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 13, 20))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 13, 50))      

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertNotIn(self.appointment, result)

    # Same overlapping time slot as the first conflict test, but for another barber.
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

    # Same overlapping time slot; only the status differs, so it must not count.
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
    # Contrast case: without exclude_appointment, the same appointment is returned.
    def test_appointment_is_conflict_without_exclude_appointment(self):
        start_base = timezone.make_aware(datetime(2026, 10, 25, 14, 15))
        end_base = timezone.make_aware(datetime(2026, 10, 25, 14, 45)) 

        result = find_conflicting_appointments(
            employee=self.employee_base,
            start=start_base,
            end=end_base
        )

        self.assertIn(self.appointment, result)

    # Editing case: the appointment must not conflict with itself.
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
    # The second appointment starts at 14:40, right after the first one's buffer, and both overlap 14:15-14:45.
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

    # No services: the end falls back to the start, so it only reserves the buffer (16:00-16:10).
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
    """Tests for the text representation of an appointment."""
    def setUp(self):
        self.client_base = Client.objects.create(name="Ana", email="ana@gmail.com")
        self.employee_base = Employee.objects.create(name="João", email="joao@gmail.com")
        self.service_base = Service.objects.create(name="Degradê", duration=timedelta(minutes=30), price=20)

    # The database stores UTC; the text must show local time (14:00, not 17:00).
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

    # Without services there is no end time, so a notice is shown instead.
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