from django.contrib import admin
from apps.appointments.models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'employee', 'display_services', 'start_time', 'end_time', 'status', 'total_duration')

    list_filter = ('status', 'start_time')

    search_fields = ('client__name', 'employee__name')

    @admin.display(description='Serviços')
    def display_services(self, obj):
        return ", ".join(service.name for service in obj.services.all())

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('client', 'employee').prefetch_related('services')
    
