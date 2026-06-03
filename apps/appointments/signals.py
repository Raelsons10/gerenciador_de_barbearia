from apps.appointments.models import Appointment
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.db.models import Sum
import datetime

# Signals para calcular automaticamente a duração total de um agendamento.
@receiver(m2m_changed, sender=Appointment.services.through)
def calculate_sum_services(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        result = instance.services.aggregate(total_time=Sum('duration'))
        instance.total_duration = result['total_time'] or datetime.timedelta()

        instance.save(update_fields=['total_duration'])
