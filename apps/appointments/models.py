from django.db import models
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
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL)
    services = models.ManyToManyField(Service)
    status = models.CharField(choices=StatusAppointment.choices, default=StatusAppointment.AGENDADO, max_length=50)
    time = models.DateTimeField(verbose_name='Data do agendamento', default=timezone.now, blank=False, null=False)
    observation = models.TextField(verbose_name='Observações', blank=True)

    # Coletando dados da duração do agendamento
    start_time = models.DateTimeField()
    duration = models.DurationField()
    end_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.start_time and self.duration:
            self.end_time = self.start_time + self.duration

        super().save(*args, **kwargs)


    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['-time']

    def __str__(self):
        return f"{self.client} - {self.time.strftime('%d/%m/%Y %H:%M')}"
    

