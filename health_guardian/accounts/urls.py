from django.urls import path
from . import views

urlpatterns = [

    path('user-change-password/', views.userPasswordChange, name='user_change_password' ),
    path('activate-email/<uidb64>/<token>', views.activateEmail, name='activate_email' ),
    path('reset-password-email/<uidb64>/<token>', views.userPasswordResetActivation, name='reset_password_email' ),
    path('user-logout/', views.userLogout, name='logout'),
    path('user-password-reset/', views.userPasswordReset, name='password_reset'),

    path('patient-signup/', views.patientSignup, name='patient_signup' ),
    path('patient-login/', views.patientLogin, name='patient_login' ),

    path('doctor-notapproved/', views.doctorBeforeApproval, name='doctor_notapproved'),
    path('doctor-signup/', views.doctorSignup, name='doctor_signup'),
    path('doctor-login/', views.doctorLogin, name='doctor_login'),

    path('admin-signup/', views.adminSignup, name='admin_signup'),
    path('admin-login/', views.adminLogin, name='admin_login')
]