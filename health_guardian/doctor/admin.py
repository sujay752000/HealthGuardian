from django.contrib import admin
from .models import ClinicAppointmnetTimings, ClinicDetails, DoctorOffDays, OnlineConsultationTimings, DoctorPredictedDisease
# Register your models here.

admin.site.register(ClinicAppointmnetTimings)
admin.site.register(ClinicDetails)
admin.site.register(DoctorOffDays)
admin.site.register(OnlineConsultationTimings)
admin.site.register(DoctorPredictedDisease)
