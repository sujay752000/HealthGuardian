from django.db import models
from django.contrib.auth.models import User

# Create your models here.


SPECIALIZATIONS = [
    ('Cardiology', 'Cardiology'),
    ('Neurology', 'Neurology'),
    ('Dermatology', 'Dermatology'),
    ('Orthopedics', 'Orthopedics'),
    ('Ophthalmology', 'Ophthalmology'),
    ('Pediatrics', 'Pediatrics'),
    ('Oncology', 'Oncology'),
    ('Gynecology', 'Gynecology'),
    ('Urology', 'Urology'),
    ('Endocrinology', 'Endocrinology'),
    ('Gastroenterology', 'Gastroenterology'),
    ('Hematology', 'Hematology'),
    ('Nephrology', 'Nephrology'),
    ('Pulmonology', 'Pulmonology'),
    ('Rheumatology', 'Rheumatology'),
    ('Allergy and Immunology', 'Allergy and Immunology'),
    ('Anesthesiology', 'Anesthesiology'),
    ('Diagnostic Radiology', 'Diagnostic Radiology'),
    ('Emergency Medicine', 'Emergency Medicine'),
    ('Family Medicine', 'Family Medicine'),
    ('Internal Medicine', 'Internal Medicine'),
    ('Medical Genetics', 'Medical Genetics'),
    ('Nuclear Medicine', 'Nuclear Medicine'),
    ('Obstetrics and Gynecology', 'Obstetrics and Gynecology'),
    ('Pathology', 'Pathology'),
    ('Physical Medicine and Rehabilitation', 'Physical Medicine and Rehabilitation'),
    ('Preventive Medicine', 'Preventive Medicine'),
    ('Psychiatry', 'Psychiatry'),
    ('Radiation Oncology', 'Radiation Oncology'),
    ('Surgery', 'Surgery'),
    ('Thoracic Surgery', 'Thoracic Surgery'),
    ('Urology', 'Urology'),
    ('Vascular Surgery', 'Vascular Surgery'),
]

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=200, choices=SPECIALIZATIONS, default='Cardiology')
    qualification_certificate = models.ImageField(upload_to='accounts/doctor_certificates/')
    experiance = models.PositiveSmallIntegerField()
    resume = models.ImageField(upload_to="accounts/doctor_resumes/")
    admin_approved = models.BooleanField(default=False)

    
