from django.contrib import admin
from .models import PatientProfile, PatientPredictedDisease, PatientBookedAppointment, OnlineConsultationPassKeys

# Register your models here.

admin.site.register(PatientProfile)
admin.site.register(PatientPredictedDisease)
admin.site.register(PatientBookedAppointment)
admin.site.register(OnlineConsultationPassKeys)



