import datetime
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from apps.clients.models import Client
from apps.services.models import Service
from apps.employees.models import Employee

# The values ​​stored in the database are in English; the displayed labels are in Portuguese.
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

    # Sum of service durations. Not editable: it is recalculated by the signal
    # whenever the appointment's services change.
    total_duration = models.DurationField(default=datetime.timedelta, editable=False)

    # The duration is only recalculated when the appointment's services change. If the
    # duration of a service changes later, existing appointments are not
    # altered: the client chose that specific time slot.
    def update_duration(self):
        """
        Recalculates total_duration by summing the durations of the services in the appointment.

        Called by a signal whenever the services change. Uses update() instead of save() to write only this column, avoiding other side effects of save() side effects and preventing other fields from being overwritten with outdated values.
        """

        # Without a pk the appointment has not been saved yet, so there are no services to add up.
        if not self.pk:
            return
        
        total = self.services.aggregate(total=Sum('duration'))['total']

        # aggregate returns None when there are no services; in this case, the duration is zero.
        self.total_duration = total or datetime.timedelta()

        Appointment.objects.filter(pk=self.pk).update(total_duration=self.total_duration)

    @property
    def end_time(self):
        """
        End of the appointment: start time plus the duration of the services.

        This is a property, not a database column, so it cannot be used in database filters. It returns None when there is no duration (an appointment with no services), because a zero-value timedelta evaluates to False in the condition below.   
        """
        if self.start_time and self.total_duration:
            return self.start_time + self.total_duration
        return None

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ['-start_time']

    def __str__(self):
        # The database stores data in UTC; convert to the project's time zone before formatting.
        moment = timezone.localtime(self.start_time)
        date = moment.strftime('%d/%m/%Y')
        start = moment.strftime('%H:%M')

        if self.end_time is not None:
            end_moment = timezone.localtime(self.end_time)
            end = end_moment.strftime('%H:%M') 
            
            return f"{self.client.name} | {self.employee.name} | {date} {start} às {end}"
        else:
            # Without services, there is no end to show.
            return f"{self.client.name} | {self.employee.name} | {date} {start} | Sem serviços"