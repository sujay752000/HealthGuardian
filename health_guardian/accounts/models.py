from django.db import models
from django.contrib.auth.models import User

# Create your models here.


SPECIALIZATIONS = [
    ('Dermatology', 'Dermatology'),
    ('Allergy and Immunology', 'Allergy and Immunology'),
    ('Gastroenterology', 'Gastroenterology'),
    ('Hepatology', 'Hepatology'),
    ('Pharmacology', 'Pharmacology'),
    ('Pulmonology', 'Pulmonology'),
    ('Cardiology', 'Cardiology'),
    ('Endocrinology', 'Endocrinology'),
    ('Neurology', 'Neurology'),
    ('Orthopedics', 'Orthopedics'),
    ('Internal Medicine', 'Internal Medicine'),
    ('Vascular Medicine', 'Vascular Medicine'),
    ('Rheumatology', 'Rheumatology'),
    ('Urology', 'Urology'),
    ('Physician', 'Physician'),
    ('Pediatrician', 'Pediatrician'),
    ('Gynecology', 'Gynecology'),
    ('Ophthalmology', 'Ophthalmology'),
    ('Otolaryngology', 'Otolaryngology'),
    ('General Surgery', 'General Surgery'),
    ('Oncology', 'Oncology')
]


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="accounts/doctor_profile_photo/")
    specialization = models.CharField(max_length=200, choices=SPECIALIZATIONS, default='Cardiology')
    qualification_certificate = models.FileField(upload_to='accounts/doctor_certificates/')
    experiance = models.PositiveSmallIntegerField()
    resume = models.FileField(upload_to="accounts/doctor_resumes/")
    admin_approved = models.BooleanField(default=False)



    def __str__(self) -> str:
        return f"{self.user.first_name} - {self.specialization}"

