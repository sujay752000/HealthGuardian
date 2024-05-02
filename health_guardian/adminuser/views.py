from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import is_admin, is_patient, is_doctor
from accounts.models import DoctorProfile
from patient.models import PatientProfile, PatientBookedAppointment
from django.core.mail import EmailMessage
from health_guardian.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .forms import AdminDoctorProfileViewForm, AdminDoctorUserViewForm
from doctor.models import ClinicDetails, ClinicAppointmnetTimings, OnlineConsultationTimings
from django.core.paginator import Paginator
from django.db.models import Q


# Create your views here.
@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminDashboard(request):
    user = request.user
    doctor_onhold_count = DoctorProfile.objects.filter(admin_approved=False).count()
    doctor_count = DoctorProfile.objects.filter(admin_approved=True).count()
    patient_count = PatientProfile.objects.all().count()

    details = {
        'user' : user,
        'doctor_onhold_count' : doctor_onhold_count,
        'doctor_count' : doctor_count,
        'patient_count' : patient_count
    }

    return render(request, "admin-app/admin_dashboard.html", context=details)


@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminDoctorOnHold(request):
    name = request.GET.get('doctor_name')
    if name:
        doctors = DoctorProfile.objects.filter(Q(admin_approved=False) & (Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name))).order_by('-user__date_joined')
    else:
        doctors = DoctorProfile.objects.filter(admin_approved=False).order_by('-user__date_joined')

    paginator = Paginator(doctors, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin-app/admin_doctor_approval.html", {"page_obj": page_obj})



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminDoctorApprove(request, pk):
    doctor = get_object_or_404(DoctorProfile, id=pk, admin_approved=False)
    doctor_name = doctor.user.get_full_name()
    doctor_email = doctor.user.email
    doctor.admin_approved = True
    doctor.save()

    # email about account access
    Subject = "Congratualations your account is verified"
    message = render_to_string('admin-app/admin_account_approval_email.html', {
        'name' : doctor_name,
        'domain' : get_current_site(request).domain,
        'protocol': 'https' if request.is_secure() else 'http'

    })

    email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[doctor_email])
    email.content_subtype = 'html'
    email.send(fail_silently=True)

    messages.success(request, f"Approved doctor {doctor_name}")
    
    return redirect("admin_doctor_onhold")



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminDoctorReject(request, pk):
    doctor = get_object_or_404(DoctorProfile, id=pk)
    doctor_name = doctor.user.get_full_name()
    user = doctor.user
    doctor.delete()
    user.delete()

    messages.success(request, f"Rejected doctor {doctor_name}")

    return redirect("admin_doctor_onhold")



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminDoctorView(request, pk):
    doctor = get_object_or_404(DoctorProfile, id=pk, admin_approved=False)
    user_form = AdminDoctorUserViewForm(instance=doctor.user)
    doctor_form = AdminDoctorProfileViewForm(instance=doctor)

    return render(request, "admin-app/admin_doctor_view.html", {'doctor': doctor, 'user_form': user_form, 'doctor_form': doctor_form})



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminDoctorApproved(request):

    name = request.GET.get('doctor_name')
    if name:
        doctors = DoctorProfile.objects.filter(Q(admin_approved=True) & (Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name))).order_by('-user__date_joined')
    else:
        doctors = DoctorProfile.objects.filter(admin_approved=True).order_by('-user__date_joined')

    paginator = Paginator(doctors, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin-app/admin_doctor_approved.html", {"page_obj": page_obj})



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminDoctorProfile(request, pk):
    doctor = get_object_or_404(DoctorProfile, id=pk)
    user = doctor.user
    clinic = ClinicDetails.objects.get(doctor=doctor)
    clinic_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor)
    online_timings = OnlineConsultationTimings.objects.filter(doctor=doctor)

    details = {
        'user': user,
        'doctor': doctor,
        'clinic': clinic,
        'clinic_timings': clinic_timings,
        'online_timings': online_timings
    }

    return render(request, "admin-app/admin_doctor_profile_view.html", context=details)




@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminPatientList(request):
    name = request.GET.get('patient_name')
    if name:
        patients = PatientProfile.objects.filter((Q(patient__first_name__icontains=name) | Q(patient__last_name__icontains=name))).order_by('-patient__date_joined')
    else:
        patients = PatientProfile.objects.all().order_by('-patient__date_joined')

    paginator = Paginator(patients, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "admin-app/admin_patient_list.html", {"page_obj": page_obj})



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminPatientProfile(request, pk):
    patient = get_object_or_404(PatientProfile, id=pk)
    user = patient.patient
    patient_bookings = PatientBookedAppointment.objects.filter(patient=patient).order_by('-date').all()

    paginator = Paginator(patient_bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    details = {
        'user': user,
        'patient': patient,
        'page_obj': page_obj
    }

    return render(request, "admin-app/admin_patient_profile_view.html", context=details)




@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminPatientRemove(request, pk):
    patient_profile = get_object_or_404(PatientProfile, id=pk)
    patient = patient_profile.patient
    patient_name = patient.get_full_name()
    patient.delete()

    messages.success(request, f"Removed patient {patient_name}")

    return redirect("admin_patient_list")



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminClinicAppointmentList(request):
    user_booking_id = request.GET.get('booking_id')
    if user_booking_id:
        bookings = PatientBookedAppointment.objects.filter(Q(booking_id__icontains=user_booking_id), appointment_type=1, payment_status=1).order_by('-date').all()
    else:
        bookings = PatientBookedAppointment.objects.filter(appointment_type=1, payment_status=1).order_by('-date')

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "admin-app/admin_clinic_appointments_list.html", {"page_obj": page_obj})



@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminAppointmentRemove(request, pk, booking_id):
    booking = get_object_or_404(PatientBookedAppointment, id=pk, booking_id=booking_id)
    if booking:
        booking_id_deleted = booking.booking_id
        booking.delete()
        messages.success(request, f"Successfully removed appointment booking id : {booking_id_deleted}")
        if booking.appointment_type == 1:
            return redirect("admin_clinic_appointments")
        else:
            return redirect("admin_online_appointments")
    else:
        messages.error(request, "Invalid Appointment Details")
        if booking.appointment_type == 1:
            return redirect("admin_clinic_appointments")
        else:
            return redirect("admin_online_appointments")


@login_required(login_url='admin_login')
@user_passes_test(is_admin)
def adminOnlineAppointmentList(request):
    user_booking_id = request.GET.get('booking_id')
    if user_booking_id:
        bookings = PatientBookedAppointment.objects.filter(Q(booking_id__icontains=user_booking_id), appointment_type=2, payment_status=1).order_by('-date').all()
    else:
        bookings = PatientBookedAppointment.objects.filter(appointment_type=2, payment_status=1).order_by('-date')

    paginator = Paginator(bookings, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "admin-app/admin_online_appointments_list.html", {"page_obj": page_obj})


