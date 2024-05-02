from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from patient.models import OnlineConsultationPassKeys
from accounts.views import is_patient, is_doctor, is_admin, dashboardRedirector
from django.contrib import messages

# Create your views here.



@login_required(login_url='app_home')
def userVideoCall(request):
    booking_id = request.GET.get('booking_id')
    doctor_id = request.GET.get('doctor_id')
    patient_id = request.GET.get('patient_id')
    pass_key_obj = get_object_or_404(OnlineConsultationPassKeys, booking_instance=booking_id, doctor=doctor_id, patient=patient_id )
    if pass_key_obj:
        extended_template = None
        if is_admin(request.user):
            extended_template = "admin-app/admin_dashboard.html"
        elif is_patient(request.user):
            extended_template = "patient-app/patient_dashboard.html"
        elif is_doctor(request.user):
            extended_template = "doctor-app/doctor_dashboard.html"
        name = request.user.get_full_name()
        return render(request, 'video_call.html', {'name': name, 'extended_template': extended_template})
    else:
        messages.error(request, "Invalid Meeting")
        return dashboardRedirector(request.user)


