from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard', views.adminDashboard, name="admin_dashboard" ),
    path('admin-doctorlist', views.adminDoctorApproved, name="admin_doctor_list" ),
    path('admin-doctor-profile/<int:pk>', views.adminDoctorProfile, name="admin_doctor_profile" ),
    path('admin-doctor-onhold', views.adminDoctorOnHold, name="admin_doctor_onhold" ),
    path('admin-doctor-approve/<int:pk>', views.adminDoctorApprove, name="admin_doctor_approve" ),
    path('admin-doctor-view/<int:pk>', views.adminDoctorView, name="admin_doctor_view" ),
    path('admin-doctor-reject/<int:pk>', views.adminDoctorReject, name="admin_doctor_reject" ),
]


