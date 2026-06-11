from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome do serviço")
    description = models.TextField(verbose_name="Descrição", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    active = models.BooleanField(default=True, verbose_name="Ativo")
    duration = models.DurationField()

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ['-price']

    def __str__(self):
        return f'{self.name} - R${self.price}'


