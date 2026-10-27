
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

    new_reserved_until = end + buffer

    list_appointments = []

    for appointment in appointments:
        end_time = appointment.end_time

        if end_time is not None:
            end_time_effective = end_time
        else:
            end_time_effective = appointment.start_time

        end_reserved_for_existing_appointment = end_time_effective + buffer

        if start < end_reserved_for_existing_appointment and appointment.start_time < new_reserved_until:
            list_appointments.append(appointment)
    return list_appointments
            
        