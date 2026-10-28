from apps.appointments.models import Appointment
from django.dispatch import receiver
from django.db.models.signals import m2m_changed

# Only handles changes made from the appointment side (appointment.services.add).
@receiver(m2m_changed, sender=Appointment.services.through)
def update_appointment_duration(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        instance.update_duration()
