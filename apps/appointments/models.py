import datetime
from django.db import models
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

    # coletando dados do início do agendamento.
    start_time = models.DateTimeField()

    # Coletando dados da duração do agendamento.
    total_duration = models.DurationField(default=datetime.timedelta, editable=False)
    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.client} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
       