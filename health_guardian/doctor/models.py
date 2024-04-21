from django.db import models
from django.contrib.auth.models import User
from accounts.models import DoctorProfile

# Create your models here.

WEEK = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday')
]

class ClinicDetails(models.Model):
    doctor = models.OneToOneField(DoctorProfile, on_delete=models.CASCADE)
    clinic_name = models.CharField(max_length=100)
    consultation_fee = models.PositiveIntegerField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.doctor} - {self.clinic_name}"


class ClinicAppointmnetTimings(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    day =  models.CharField(max_length=100, choices=WEEK)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.doctor} - {self.day}"

class OnlineConsultationTimings(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    day =  models.CharField(max_length=100, choices=WEEK)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.doctor} - {self.day}"


class DoctorOffDays(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    date = models.DateField(unique=True)

    def __str__(self) -> str:
        return f"{self.doctor} - {self.date}"


