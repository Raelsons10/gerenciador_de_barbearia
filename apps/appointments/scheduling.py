
from django.conf import settings
from apps.appointments.models import Appointment, StatusAppointment

def find_conflicting_appointments(employee, start, end, exclude_appointment=None, buffer=None):

    """
    Returns a barber's appointments that conflict with a given time slot.

    Only appointments with a 'scheduled' status are considered; cancelled or completed appointments do not occupy the schedule. Each appointment also reserves a buffer period after its end time (APPOINTMENT_BUFFER). This buffer applies in both directions: the new time slot also reserves a buffer period following its own end time.

    Args:
        employee: The barber whose schedule is being checked.
        start, end: The start and end times of the proposed appointment.
        exclude_appointment: An appointment to be ignored, used during editing to prevent an appointment from conflicting with itself.
        buffer: A time interval (timedelta) to be reserved after each appointment.
        If set to None, the APPOINTMENT_BUFFER from settings is used.

    Returns:
        A list of conflicting appointments (empty if none are found).    
    """

    # Uses the default interval from settings when none is provided.
    if buffer is None:
        buffer = settings.APPOINTMENT_BUFFER

    # Filter by barber and only scheduled appointments; cancelled and completed ones free up the time slot.
    appointments = Appointment.objects.filter(
        employee=employee,
        status=StatusAppointment.AGENDADO
    )

    # When editing, the appointment cannot conflict with itself.
    if exclude_appointment is not None:
        appointments = appointments.exclude(pk=exclude_appointment.pk)

    # The new schedule also sets aside an interval after it ends.
    new_reserved_until = end + buffer

    list_appointments = []

    # Perform the comparison in Python, because end_time is a property and does not exist as a column in the database.
    for appointment in appointments:
        end_time = appointment.end_time

        # Without services, there is no duration, so the end falls back to the start time and the appointment reserves only the buffer.
        if end_time is not None:
            end_time_effective = end_time
        else:
            end_time_effective = appointment.start_time

        end_reserved_for_existing_appointment = end_time_effective + buffer

        # A conflict happens when each appointment starts before the other one (plus its buffer) has ended.
        if start < end_reserved_for_existing_appointment and appointment.start_time < new_reserved_until:
            list_appointments.append(appointment)
    return list_appointments
            
        