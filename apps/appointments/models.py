import datetime
from django.db import models
from django.db.models import Sum
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from apps.clients.models import Client
from apps.services.models import Service
from apps.employees.models import Employee



class StatusAppointment(models.TextChoices):
    AGENDADO = 'scheduled', 'Agendado'
    CONCLUIDO = 'completed', 'Concluído'
    CANCELADO = 'cancelled', 'Cancelado'

class Appointment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    services = models.ManyToManyField(Service)
    status = models.CharField(choices=StatusAppointment.choices, default=StatusAppointment.AGENDADO, max_length=50)
    observation = models.TextField(verbose_name='Observações', blank=True)

    # coletando dados do início e fim do agendamento.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True, editable=False)

    # Coletando dados da duração do agendamento.
    total_duration = models.DurationField(default=datetime.timedelta, editable=False)
    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.client} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
    
    # Signals para calcular automaticamente a duração total de um agendamento.
@receiver(m2m_changed, sender=Appointment.services.through)
def calculate_sum_services(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        result = instance.services.aggregate(total_time=Sum('duration'))
        instance.total_duration = result['total_time'] or datetime.timedelta()

        if instance.start_time:
            instance.end_time = instance.start_time + instance.total_duration
        else:
            instance.end_time = None

        instance.save(update_fields=['total_duration', 'end_time'])
