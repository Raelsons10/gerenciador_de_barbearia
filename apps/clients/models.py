from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nome')
    phone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(unique=True)
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Data')

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.phone}'

