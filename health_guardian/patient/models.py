from django.db import models
from django.contrib.auth.models import User

# Create your models here.

GENDER = [
    ('male', 'male'),
    ('female', 'female'),
    ('others', 'others')
]

class PatientProfile(models.Model):
    patient = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.ImageField(upload_to="patient/patient_profile_photo/")
    address = models.TextField(max_length=600)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=50, choices=GENDER, default='male')
    height = models.PositiveIntegerField()
    weight = models.PositiveIntegerField()
    previous_illness = models.TextField(max_length=800, null=True, blank=True)
    chronic_diseases = models.TextField(max_length=800, null=True, blank=True)


    def __str__(self) -> str:
        return f"{self.patient.first_name}"
    

class PatientPredictedDisease(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    symptoms = models.CharField(max_length=2000)
    model = models.CharField(max_length=100)
    disease = models.CharField(max_length=500)
    date = models.DateField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.patient} - {self.disease}"
    
