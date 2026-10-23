
from django.conf import settings
from apps.appointments.models import Appointment, StatusAppointment

def find_conflicting_appointments(employee, start, end, exclude_appointment=None, buffer=None):
    if buffer is None:
        buffer = settings.APPOINTMENT_BUFFER

    appointments = Appointment.objects.filter(
        employee=employee,
        status=StatusAppointment.AGENDADO
    )

    if exclude_appointment is not None:
        appointments = appointments.exclude(pk=exclude_appointment.pk)

    list_appointments = []

    for appointment in appointments:
        end_reserved_for_existing_appointment = appointment.end_time + buffer
        reserved_for_a_new_appointment = end + buffer

        if start < end_reserved_for_existing_appointment and appointment.start_time < reserved_for_a_new_appointment:
            list_appointments.append(appointment)
    return list_appointments
            
        