from django.db import models
from patient.models import OnlineConsultationPassKeys
from django.contrib.auth.models import User
from accounts.views import is_admin, is_patient, is_doctor
from patient.models import PatientProfile
from accounts.models import DoctorProfile
from datetime import datetime
# Create your models here.


class Message(models.Model):
    room = models.ForeignKey(OnlineConsultationPassKeys, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(null=True, blank=True)  # Add timestamp to track message time

    def __str__(self):
        return f"{self.room.pass_key}-{self.timestamp}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # If the object is not saved yet
            self.timestamp = datetime.now()  # Store the current local time
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('timestamp',)
    

    def sender_photo(self):
        if is_admin(self.sender):
            return None 
        elif is_patient(self.sender):
            patient_profile = PatientProfile.objects.get(patient=self.sender)
            return patient_profile.photo
        elif is_doctor(self.sender):
            doctor_profile = DoctorProfile.objects.get(user=self.sender)
            return doctor_profile.photo
        else:
            return None 

