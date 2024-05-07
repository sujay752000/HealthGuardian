from django.urls import path
from . import views

urlpatterns = [
    path('doctor-dashboard', views.doctorDashboard, name="doctor_dashboard" ),
    path('doctor-disease-predict', views.doctorDiseasePredict, name="doctor_disease_predict" ),
    path('doctor-diet-precautions', views.doctorDietPrecautionView, name="doctor_diet_precautions" ),
    path('doctor-diet/<str:disease>', views.doctorDietChart, name="doctor_diet" ),
    path('doctor-precaution/<str:disease>', views.doctorPrecaution, name="doctor_precaution" ),
    path('doctor-profile-update', views.doctorProfileUpdate, name="doctor_profile_update" ),
    path('doctor-clinic-profile', views.doctorClinicRegister, name="doctor_clinic_profile" ),
    path('doctor-online-profile', views.doctorOnlineConsultationRegister, name="doctor_online_profile" ),
    path('doctor-timings-update', views.doctorTimingsUpdate, name="doctor_timings_update" ),
    path('doctor-clinic-timings-update', views.doctorClinicTimingsUpdate, name="doctor_clinic_timings_update" ),
    path('doctor-online-timings-update', views.doctorOnlineTimingsUpdate, name="doctor_online_timings_update" ),
    path('doctor-offdays-register', views.doctorOffDaysRegister, name="doctor_offdays_register" ),
    path('doctor-offdays-remove/<int:day>', views.doctorRemoveOffDays, name="doctor_offdays_remove" ),
    path('doctor-clinical-appointments', views.doctorClinicalAppointments, name="doctor_clinical_appointments" ),
    path('doctor-online-appointments', views.doctorOnlineAppointments, name="doctor_online_appointments" ),
    path('doctor-patient-profile/<int:pk>', views.doctorPatientViewProfile, name="doctor_patient_profile" ),
    # path('doctor-room', views.doctorVideoCall, name="doctor_room" ),
    path('doctor-room-join/<int:booking_id>/<int:doctor_id>/<int:patient_id>', views.doctorJoinCall, name="doctor_room_join" ),
    path('doctor-consultation-options/<int:booking_id>/<int:doctor_id>/<int:patient_id>', views.doctorOnlineConsultationOptions, name="doctor_consultation_options" ),
    path('doctor-videocall-option/<int:booking_id>/<int:doctor_id>/<int:patient_id>', views.doctorVideoCallOption, name="doctor_videocall_option" ),
    path('doctor-chat-option/<int:booking_id>/<int:doctor_id>/<int:patient_id>', views.doctorChatOption, name="doctor_chat_option" ),
    path('doctor-chat-assistant', views.doctorChatAssistant, name="doctor_chat_assistant" ),
]

