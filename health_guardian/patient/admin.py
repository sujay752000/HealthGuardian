from django.contrib import admin
from .models import PatientProfile, PatientPredictedDisease

# Register your models here.

admin.site.register(PatientProfile)
admin.site.register(PatientPredictedDisease)
