from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from .models import Prescription, Event


class PrescriptionTests(TestCase):
    """Test Prescription model"""
    
    def test_create_prescription(self):
        """Can create a valid prescription"""
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
        """Future DOB should be rejected"""
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
        """Name with only numbers should fail"""
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


class EventTests(TestCase):
    """Test Event model"""
    
    def setUp(self):
        """Create a prescription for testing"""
        self.prescription = Prescription.objects.create(
            patient_name="Test Patient",
            patient_dob=date(1990, 1, 1),
            medication_name="Test Med",
            medication_dose="10mg",
            medication_order_date=date.today()
        )
    
    def test_create_event(self):
        """Can create an event"""
        event = Event.objects.create(
            prescription=self.prescription,
            performed_by="JD",
            event_type="NOTE",
            description="Test note"
        )
        self.assertEqual(event.performed_by, "JD")
    
    def test_event_updates_prescription_timestamp(self):
        """Creating event updates prescription updated_at"""
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
    """Test complete workflows"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_dashboard_shows_prescriptions(self):
        """Dashboard displays prescriptions"""
        # Create prescription
        Prescription.objects.create(
            patient_name="Test Patient",
            patient_dob=date(1990, 1, 1),
            medication_name="Test Med",
            medication_dose="10mg",
            medication_order_date=date.today()
        )
        
        # Visit dashboard
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Patient")
    
    def test_add_event_workflow(self):
        """Can add event through the UI"""
        # Create prescription
        prescription = Prescription.objects.create(
            patient_name="Test Patient",
            patient_dob=date(1990, 1, 1),
            medication_name="Test Med",
            medication_dose="10mg",
            medication_order_date=date.today()
        )
        
        # Add event via POST
        response = self.client.post(
            reverse('prescription_detail', kwargs={'pk': prescription.pk}),
            {
                'performed_by': 'JD',
                'event_type': 'NOTE',
                'description': 'Test event'
            }
        )
        
        # Should redirect after success
        self.assertEqual(response.status_code, 302)
        
        # Event should exist
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.description, "Test event")