from django.urls import path
from . import views

urlpatterns = [
    path('patient-dashboard', views.patientDashboard, name="patient_dashboard" ),
    path('patient-profile', views.patientProfileRegister, name="patient_profile" ),
    path('patient-predict-disease', views.patientDiseasePredict, name="patient_predict_disease" ),
    path('patient-update', views.patientProfileUpdate, name="patient_update" ),
    path('patient-doctor-search', views.patientSearchDoctors, name="patient_doctor_search" ),
    path('patient-doctor-profileview/<int:pk>', views.patientDoctorProfileView, name="patient_doctor_profileview" ),
    path('patient-doctor-book/<int:doctor>', views.patientBookAppointmentView, name="patient_doctor_book" ),
    path('patient-diet-precautions', views.patientDietPrecautionView, name="patient_diet_precautions" ),
    path('patient-diet/<str:disease>', views.patientDietChart, name="patient_diet" ),
    path('patient-precaution/<str:disease>', views.patientPrecaution, name="patient_precaution" ),
]

