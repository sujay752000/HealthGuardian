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
    path('patient-clinic-appointment_date/<int:doctor_id>/<int:patient_id>', views.patientClinicBookAppointmeentDate, name="patient_clinic_appointment_date" ),
    path('patient-online-appointment_date/<int:doctor_id>/<int:patient_id>', views.patientOnlineBookAppointmeentDate, name="patient_online_appointment_date" ),
    path('patient-clinic-appointment_time/<int:doctor_id>/<int:patient_id>/<str:date>', views.patientClinicBookAppointmentTime, name="patient_clinic_appointment_time" ),
    path('patient-online-appointment_time/<int:doctor_id>/<int:patient_id>/<str:date>', views.patientOnlineBookAppointmentTime, name="patient_online_appointment_time" ),
    path('patient-diet-precautions', views.patientDietPrecautionView, name="patient_diet_precautions" ),
    path('patient-diet/<str:disease>', views.patientDietChart, name="patient_diet" ),
    path('patient-precaution/<str:disease>', views.patientPrecaution, name="patient_precaution" ),
    path('patient-payment-handler', views.patientPaymentHandleRequest, name="patient_payment_handler" ),
    path('patient-online-consultations', views.patientOnlineConsultationTable, name="patient_online_consultations" ),
    path('patient-clinic-consultations', views.patientClinicConsultationTable, name="patient_clinic_consultations" ),
    path('patient-room-details', views.patientVideoCallView, name="patient_room_details" ),
    path('patient-room', views.patientVideoCall, name="patient_room" ),
    path('patient-room-join/<int:booking_id>/<int:doctor_id>/<int:patient_id>', views.patientJoinCall, name="patient_room_join" ),
    path('patient-chat-assistant', views.patientChatAssistant, name="patient_chat_assistant" ),
]


