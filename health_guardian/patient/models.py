from django.db import models
from django.contrib.auth.models import User
from accounts.models import DoctorProfile
from django.utils import timezone

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
        return f"{self.patient.get_full_name()}"
    


class PatientPredictedDisease(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    symptoms = models.CharField(max_length=2000)
    model = models.CharField(max_length=100)
    disease = models.CharField(max_length=500)
    date = models.DateField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.patient} - {self.disease}"




payment_status_codes = (
    (1, 'SUCCESS'),
    (2, 'FAILURE'),
    (3, 'PENDING'),
) 


appointment_type_codes = (
    (1, 'CLINIC'),
    (2, 'ONLINE'),
)


class PatientBookedAppointment(models.Model):
    booking_id = models.CharField(max_length=500)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    appointment_type = models.PositiveIntegerField(choices=appointment_type_codes)
    date = models.DateField()
    time = models.CharField(max_length=100)
    consulting_fee = models.PositiveBigIntegerField()
    payment_status = models.PositiveIntegerField(choices=payment_status_codes, default=3)
    datetime_of_payment = models.DateTimeField(default=timezone.now)

    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)


    def __str__(self) -> str:
        return f"{self.patient}-{self.booking_id}"
    

class OnlineConsultationPassKeys(models.Model):
    booking_instance = models.OneToOneField(PatientBookedAppointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    pass_key = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.booking_instance}-{self.pass_key}"
    