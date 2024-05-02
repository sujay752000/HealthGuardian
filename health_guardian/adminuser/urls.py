from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard', views.adminDashboard, name="admin_dashboard" ),
    path('admin-doctorlist', views.adminDoctorApproved, name="admin_doctor_list" ),
    path('admin-patientlist', views.adminPatientList, name="admin_patient_list" ),
    path('admin-doctor-profile/<int:pk>', views.adminDoctorProfile, name="admin_doctor_profile" ),
    path('admin-doctor-onhold', views.adminDoctorOnHold, name="admin_doctor_onhold" ),
    path('admin-doctor-approve/<int:pk>', views.adminDoctorApprove, name="admin_doctor_approve" ),
    path('admin-doctor-view/<int:pk>', views.adminDoctorView, name="admin_doctor_view" ),
    path('admin-patient-view/<int:pk>', views.adminPatientProfile, name="admin_patient_view" ),
    path('admin-patient-remove/<int:pk>', views.adminPatientRemove, name="admin_patient_remove" ),
    path('admin-doctor-reject/<int:pk>', views.adminDoctorReject, name="admin_doctor_reject" ),
    path('admin-online-appointments', views.adminOnlineAppointmentList, name="admin_online_appointments" ),
    path('admin-clinic-appointments', views.adminClinicAppointmentList, name="admin_clinic_appointments" ),
    path('admin-appointment-remove/<int:pk>/<str:booking_id>', views.adminAppointmentRemove, name="admin_appointment_remove" ),
]


