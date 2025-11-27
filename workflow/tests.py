from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from .models import Prescription, Event


class PrescriptionTests(TestCase):

    def test_create_prescription(self):
        prescription = Prescription.objects.create(
            patient_name="John Doe",
            patient_dob=date(1990, 1, 1),
            medication_name="Humira",
            medication_dose="40mg",
            medication_order_date=date.today()
        )
        self.assertEqual(prescription.patient_name, "John Doe")
        self.assertEqual(prescription.status, "NEW")
    
    def test_future_dob_fails(self):
        from django.core.exceptions import ValidationError
        
        prescription = Prescription(
            patient_name="Jane Doe",
            patient_dob=date.today() + timedelta(days=1),  # Tomorrow
            medication_name="Test",
            medication_dose="10mg",
            medication_order_date=date.today()
        )
        
        with self.assertRaises(ValidationError):
            prescription.save()
    
    def test_name_must_have_letters(self):
        from django.core.exceptions import ValidationError

        prescription = Prescription(
            patient_name="12345",  # No letters
            patient_dob=date(1990, 1, 1),
            medication_name="Test",
            medication_dose="10mg",
            medication_order_date=date.today()
        )

        with self.assertRaises(ValidationError):
            prescription.save()

    def test_duplicate_prescription_blocked(self):
        from django.core.exceptions import ValidationError

        Prescription.objects.create(
            patient_name="John Doe",
            patient_dob=date(1990, 1, 1),
            medication_name="Humira",
            medication_dose="40mg",
            medication_order_date=date.today()
        )
        with self.assertRaises(ValidationError):
            Prescription.objects.create(
                patient_name="John Doe",
                patient_dob=date(1990, 1, 1),
                medication_name="Humira",
                medication_dose="20mg",  # different dose, same patient+med+date
                medication_order_date=date.today()
            )


class EventTests(TestCase):

    def setUp(self):
        self.prescription = Prescription.objects.create(
            patient_name="Test Patient",
            patient_dob=date(1990, 1, 1),
            medication_name="Test Med",
            medication_dose="10mg",
            medication_order_date=date.today()
        )
    
    def test_create_event(self):
        event = Event.objects.create(
            prescription=self.prescription,
            performed_by="JD",
            event_type="NOTE",
            description="Test note"
        )
        self.assertEqual(event.performed_by, "JD")
    
    def test_event_updates_prescription_timestamp(self):
        old_updated = self.prescription.updated_at
        
        Event.objects.create(
            prescription=self.prescription,
            performed_by="JD",
            event_type="NOTE",
            description="Test"
        )
        
        self.prescription.refresh_from_db()
        self.assertGreater(self.prescription.updated_at, old_updated)


class IntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
    
    def test_dashboard_shows_prescriptions(self):
        Prescription.objects.create(
            patient_name="Test Patient",
            patient_dob=date(1990, 1, 1),
            medication_name="Test Med",
            medication_dose="10mg",
            medication_order_date=date.today()
        )
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Patient")

    def test_add_event_workflow(self):
        prescription = Prescription.objects.create(
            patient_name="Test Patient",
            patient_dob=date(1990, 1, 1),
            medication_name="Test Med",
            medication_dose="10mg",
            medication_order_date=date.today()
        )
        response = self.client.post(
            reverse('prescription_detail', kwargs={'pk': prescription.pk}),
            {'performed_by': 'JD', 'event_type': 'NOTE', 'description': 'Test event'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.first().description, "Test event")