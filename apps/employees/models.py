from django.db import models

class Employee(models.Model):
    name = models.CharField(verbose_name="Nome",max_length=100)
    specialty = models.CharField(verbose_name="Especialidade", max_length=50)
    phone = models.CharField(verbose_name="Telefone", max_length=20)
    active = models.BooleanField(verbose_name="Ativo", default=True )
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.specialty}'    
