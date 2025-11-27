from django.shortcuts import render, get_object_or_404, redirect
from .models import Prescription, Event
from django.contrib import messages
import logging

logger = logging.getLogger('workflow')


def dashboard(request):
    prescriptions = Prescription.objects.all()
    logger.info(f"Dashboard accessed - {prescriptions.count()} prescriptions")

    for prescription in prescriptions:
        prescription.latest_event = prescription.events.first()


    context = {
        'prescriptions': prescriptions,
        'title': 'Intake Dashboard'
    }

    return render(request, 'workflow/dashboard.html', context)


def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    events = prescription.events.all()

    if request.method == 'POST':
        try:
            event = Event(
                prescription=prescription,
                performed_by=request.POST.get('performed_by', '').strip(),
                event_type=request.POST.get('event_type', 'NOTE'),
                description=request.POST.get('description', '').strip()
            )
            event.save()
            logger.info(f"Event added: {event.event_type} by {event.performed_by} for prescription {pk}")
            messages.success(request, "Event added successfully")
            return redirect('prescription_detail', pk=pk)
        except Exception as e:
            logger.error(f"Failed to add event for prescription {pk}: {str(e)}")
            messages.error(request, "Error adding event. Please check your input.")  
    
    context = {
        'prescription': prescription,
        'events': events,
        'title': f'Prescription - {prescription.patient_name}',  
        'event_types': Event.EVENT_TYPES,
    }

    return render(request, 'workflow/prescription_detail.html', context)  