from django.urls import path
from . import views

urlpatterns = [
    path('doctor-dashboard', views.doctorDashboard, name="doctor_dashboard" ),
    path('doctor-profile-update', views.doctorProfileUpdate, name="doctor_profile_update" ),
    path('doctor-clinic-profile', views.doctorClinicRegister, name="doctor_clinic_profile" ),
    path('doctor-online-profile', views.doctorOnlineConsultationRegister, name="doctor_online_profile" ),
    path('doctor-timings-update', views.doctorTimingsUpdate, name="doctor_timings_update" ),
    path('doctor-clinic-timings-update', views.doctorClinicTimingsUpdate, name="doctor_clinic_timings_update" ),
    path('doctor-online-timings-update', views.doctorOnlineTimingsUpdate, name="doctor_online_timings_update" ),
    path('doctor-offdays-register', views.doctorOffDaysRegister, name="doctor_offdays_register" ),
    path('doctor-offdays-remove/<int:day>', views.doctorRemoveOffDays, name="doctor_offdays_remove" ),
]

