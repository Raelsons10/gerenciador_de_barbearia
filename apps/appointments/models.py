import datetime
from django.db import models
from django.db.models import Sum
from apps.clients.models import Client
from apps.services.models import Service
from apps.employees.models import Employee


class StatusAppointment(models.TextChoices):
    AGENDADO = 'scheduled', 'Agendado'
    CONCLUIDO = 'completed', 'Concluído'
    CANCELADO = 'cancelled', 'Cancelado'


class Appointment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    services = models.ManyToManyField(Service)
    status = models.CharField(choices=StatusAppointment.choices, default=StatusAppointment.AGENDADO, max_length=50)
    observation = models.TextField(verbose_name='Observações', blank=True)
    start_time = models.DateTimeField()

    # Coletando dados da duração do agendamento.
    total_duration = models.DurationField(default=datetime.timedelta, editable=False)

    def update_duration(self):
        if not self.pk:
            return
        
        total = self.services.aggregate(total=Sum('duration'))['total']
        self.total_duration = total or datetime.timedelta()

        Appointment.objects.filter(pk=self.pk).update(total_duration=self.total_duration)

    # Coletando dados do fim do agendamento.
    @property
    def end_time(self):
        if self.start_time and self.total_duration:
            return self.start_time + self.total_duration
        return None

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['-start_time']

    def __str__(self):
        date = self.start_time.strftime('%d/%m/%Y')
        start = self.start_time.strftime('%H:%M')
        end = self.end_time.strftime('%H:%M') 
        return f"{self.client.name} | {self.employee.name} | {date} {start} às {end}"