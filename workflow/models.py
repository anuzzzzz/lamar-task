from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

# Create your models here.


class Prescription(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('INS_VERIFY', 'Verifying Insurance'),
        ('PA', 'Prior Auth'),
        ('INFO_REQ', 'Info Requested'),
        ('READY', 'Ready for Review'),
    ]

    patient_name = models.CharField(max_length=255)
    patient_dob = models.DateField()
    patient_phone = models.CharField(max_length=20, blank=True)  # Fixed: blank=True instead of null=True
    medication_name = models.CharField(max_length=100)  # Fixed: max_length (was max_lenth)
    medication_dose = models.CharField(max_length=100)  # Fixed: max_length (was max_lenth)
    medication_order_date = models.DateField()
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Fixed: auto_now (was auto_add)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['patient_name', 'patient_dob', 'medication_name', 'medication_order_date']

    def clean(self):
        super().clean()
        today = timezone.now().date()

        if self.patient_dob:
            if self.patient_dob > today:
                raise ValidationError({'patient_dob': 'Cannot be in future'})
            age_years = (today - self.patient_dob).days / 365
            if age_years > 100:
                raise ValidationError({'patient_dob': 'Cannot exceed 100'})
        
        if self.medication_order_date:
            if self.medication_order_date > today:
                raise ValidationError({'medication_order_date': 'Cannot be in the future'})
            if (today - self.medication_order_date).days > 365:
                raise ValidationError({'medication_order_date': 'Order date is over 1 year, please check'})
            
        if self.patient_name and not re.search(r'[a-zA-Z]', self.patient_name):
            raise ValidationError({'patient_name': 'Patient name must contain letters'})
        
        if self.patient_phone:
            cleaned = re.sub(r'[\s\-\(\)]', '', self.patient_phone)
            if not cleaned.isdigit():
                raise ValidationError({'patient_phone': 'Phone number must contain only digits, spaces, dashes, and parentheses'})
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 

    def __str__(self):
        return f"{self.patient_name} - {self.medication_name}"
            
    
class Event(models.Model):
    EVENT_TYPES = [
        ('NOTE', 'Note'),  # Fixed: added missing commas
        ('INS', 'Insurance call'),
        ('STATUS', 'Status Change'),
        ('OTHER', 'Other'),
    ]

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='events'
    )

    performed_by = models.CharField(max_length=50)
    event_type = models.CharField(max_length=100, choices=EVENT_TYPES, default='NOTE')  # Fixed: removed extra parentheses
    description = models.TextField()  # Fixed: models.TextField() instead of models.description
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def clean(self):
        super().clean()  

        if self.description and not self.description.strip():
            raise ValidationError({'description': 'Description cannot be empty'})

        if self.performed_by:
            if not self.performed_by.strip():
                raise ValidationError({'performed_by': 'Performed by(Name) cannot be empty'})
            if self.performed_by.strip().isdigit():
                raise ValidationError({'performed_by': 'Name cannot have digits'})
    
    def save(self, *args, **kwargs):  
        """Override save to enforce validation and update prescription timestamp."""
        self.full_clean()
        super().save(*args, **kwargs)
        # Trigger prescription update so it moves to top of queue
        self.prescription.save()
    
    def __str__(self):
        return f"{self.event_type} by {self.performed_by}"
