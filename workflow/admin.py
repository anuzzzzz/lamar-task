from django.contrib import admin
from .models import Prescription, Event


class EventInline(admin.TabularInline):
    model = Event
    extra = 1
    readonly_fields = ('created_at',)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'medication_name', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('patient_name', 'medication_name')
    inlines = [EventInline]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'event_type', 'performed_by', 'created_at')
    list_filter = ('event_type',)
