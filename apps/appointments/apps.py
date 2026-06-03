from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    name = 'apps.appointments'

    def ready(self):
        from . import signals