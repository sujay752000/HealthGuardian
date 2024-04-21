from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import is_admin, is_patient, is_doctor
from accounts.models import DoctorProfile
from .forms import ClinicAppointmentTimingsRegisterForm, OnlineConsultationTimingsRegisterForm, ClinicRegisterForm, DoctorOffDaysRegisterForm
from .models import ClinicDetails, ClinicAppointmnetTimings, OnlineConsultationTimings, DoctorOffDays
from django.forms import formset_factory
from .forms import BaseAppointmentFormSet, ClinicAppointmentTimingsUpdateForm, OnlineAppointmentTimingsUpdateForm, DoctorUserUpdateForm, DoctorProfileUpdateForm
from .models import WEEK, ClinicAppointmnetTimings, ClinicDetails, OnlineConsultationTimings
from django.contrib import messages
from django.core.paginator import Paginator

# Create your views here.


week = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday'
]


clinic_timings_formset = formset_factory(
    form= ClinicAppointmentTimingsRegisterForm,
    formset=BaseAppointmentFormSet,
    extra=7
)

consultation_timings_formset = formset_factory(
    form= OnlineConsultationTimingsRegisterForm,
    formset=BaseAppointmentFormSet,
    extra=7
)



def clinic_profile_completed(user):
    doctor_profile_obj = DoctorProfile.objects.get(user=user)
    doctor_clinic = ClinicDetails.objects.filter(doctor=doctor_profile_obj)
    doctor_clinic_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor_profile_obj)
    if doctor_clinic and doctor_clinic_timings:
        return True
    
def clinic_profile_not_completed(user):
    doctor_profile_obj = DoctorProfile.objects.get(user=user)
    doctor_clinic = ClinicDetails.objects.filter(doctor=doctor_profile_obj)
    doctor_clinic_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor_profile_obj)
    if not doctor_clinic and not doctor_clinic_timings:
        return True

def online_consult_completed(user):
    doctor_profile_obj = DoctorProfile.objects.get(user=user)
    doctor_consult_timings = OnlineConsultationTimings.objects.filter(doctor=doctor_profile_obj)
    if doctor_consult_timings:
        return True
    
def online_consult_not_completed(user):
    doctor_profile_obj = DoctorProfile.objects.get(user=user)
    doctor_consult_timings = OnlineConsultationTimings.objects.filter(doctor=doctor_profile_obj)
    if not doctor_consult_timings:
        return True
    





@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorDashboard(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)
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

    return render(request, "doctor-app/doctor_dashboard.html", context=details)


@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorProfileUpdate(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)
    clinic = ClinicDetails.objects.get(doctor=doctor)


    user_form = DoctorUserUpdateForm(instance=user)
    doctor_form = DoctorProfileUpdateForm(instance=doctor)
    clinic_form = ClinicRegisterForm(instance=clinic)

    details = {
        'doctor': doctor,
        'user_form': user_form,
        'doctor_form': doctor_form,
        'clinic_form': clinic_form
    }

    if request.method == 'POST':
        user_form = DoctorUserUpdateForm(request.POST, instance=user)
        doctor_form = DoctorProfileUpdateForm(request.POST, request.FILES,  instance=doctor)
        clinic_form = ClinicRegisterForm(request.POST, instance=clinic)
        
        if user_form.is_valid() and doctor_form.is_valid() and clinic_form.is_valid():
            user_form.save()
            doctor_form.save()
            if 'photo' in request.FILES:
                doctor.photo = request.FILES['photo']
                doctor.save()
            clinic_form.save()
            messages.success(request, "Successfully updated your profile")
            return redirect("doctor_dashboard")
        else:
            messages.error(request, "Invalid details")
            return render(request, "doctor-app/doctor_profile_update.html", context=details)

    return render(request, "doctor-app/doctor_profile_update.html", context=details )


@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_not_completed, login_url='doctor_dashboard')
def doctorClinicRegister(request):
        clinic_form = ClinicRegisterForm()
        clinic_timings_form = clinic_timings_formset()

        user = request.user
        doctor_obj = DoctorProfile.objects.get(user=user)

        if request.method == 'POST':
            clinic_form = ClinicRegisterForm(request.POST)
            clinic_timings_form = clinic_timings_formset(request.POST)


            if clinic_form.is_valid() and clinic_timings_form.is_valid():
                clinic_obj = clinic_form.save(commit=False)
                clinic_obj.doctor = doctor_obj
                clinic_obj.save()

                for form_no, day in zip(clinic_timings_form, week):
                    form_obj = form_no.save(commit=False)
                    form_obj.doctor = doctor_obj
                    form_obj.day = day
                    form_obj.save()

                messages.success(request, "Successfully added your clinic details and timings")
                return redirect("doctor_dashboard")

            else:
                clinic_timings_errors = clinic_timings_form.non_form_errors()
                messages.error(request, f"Invalid Details")
                zipped_clinic_timings_form = zip(clinic_timings_form, WEEK)
                return render(request, "doctor-app/doctor_clinic_register.html", {
                    'clinic_form': clinic_form,
                    'clinic_timings_form': zipped_clinic_timings_form,
                    'weekdays': WEEK,
                    'formset_management_data': clinic_timings_form.management_form,
                    'clinic_timings_errors': clinic_timings_errors,
                    })
                         
        zipped_clinic_timings_form = zip(clinic_timings_form, WEEK)
        return render(request, "doctor-app/doctor_clinic_register.html", {
            'clinic_form': clinic_form,
            'clinic_timings_form': zipped_clinic_timings_form,
            'weekdays': WEEK,
            'formset_management_data': clinic_timings_form.management_form,
            })


@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorTimingsUpdate(request):
    return render(request, "doctor-app/doctor_schedule_timings_view.html")

  

@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorClinicTimingsUpdate(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)
    clinic = ClinicDetails.objects.get(doctor=doctor)

    clinic_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor)

    clinic_form = ClinicRegisterForm(instance=clinic)
    clinic_timings_form = ClinicAppointmentTimingsUpdateForm()

    if request.method == 'POST':
        clinic_timings_form = ClinicAppointmentTimingsUpdateForm(request.POST)
        if clinic_timings_form.is_valid():
            day_obj = clinic_timings_form.cleaned_data.get('day')
            time_instance = ClinicAppointmnetTimings.objects.get(doctor=doctor, day=day_obj)
            time_instance.start_time = clinic_timings_form.cleaned_data.get('start_time')
            time_instance.end_time = clinic_timings_form.cleaned_data.get('end_time')
            time_instance.save()
            messages.success(request, "Successfully updated time schedule")
            return redirect("doctor_clinic_timings_update")
        else:
            messages.error(request, "Invalid details")
            return render(request, "doctor-app/doctor_clinic_timings_update.html", {'clinic_form': clinic_form, 'clinic_timings': clinic_timings, 'clinic_timings_form': clinic_timings_form})

    return render(request, "doctor-app/doctor_clinic_timings_update.html", {'clinic_form': clinic_form, 'clinic_timings': clinic_timings, 'clinic_timings_form': clinic_timings_form})



@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorOnlineTimingsUpdate(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)

    online_timings = OnlineConsultationTimings.objects.filter(doctor=doctor)

    online_timings_form = OnlineAppointmentTimingsUpdateForm()

    if request.method == 'POST':
        online_timings_form = OnlineAppointmentTimingsUpdateForm(request.POST)
        if online_timings_form.is_valid():
            day_obj = online_timings_form.cleaned_data.get('day')
            time_instance = OnlineConsultationTimings.objects.get(doctor=doctor, day=day_obj)
            time_instance.start_time = online_timings_form.cleaned_data.get('start_time')
            time_instance.end_time = online_timings_form.cleaned_data.get('end_time')
            time_instance.save()
            messages.success(request, "Successfully updated time schedule")
            return redirect("doctor_online_timings_update")
        else:
            messages.error(request, "Invalid details")
            return render(request, "doctor-app/doctor_online_timings_update.html", {'online_timings': online_timings, 'online_timings_form': online_timings_form})

    return render(request, "doctor-app/doctor_online_timings_update.html", {'online_timings': online_timings, 'online_timings_form': online_timings_form})




@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(online_consult_not_completed, login_url='doctor_dashboard')
def doctorOnlineConsultationRegister(request):
        online_consultation_form = consultation_timings_formset()

        user = request.user
        doctor_obj = DoctorProfile.objects.get(user=user)

        if request.method == 'POST': 
            online_consultation_form = consultation_timings_formset(request.POST)

            if online_consultation_form.is_valid():

                for form_no, day in zip(online_consultation_form, week):
                    form_obj = form_no.save(commit=False)
                    form_obj.doctor = doctor_obj
                    form_obj.day = day
                    form_obj.save()

                messages.success(request, "Successfully added your online consultation and time schedule")
                return redirect("doctor_dashboard")
            else:
                print(online_consultation_form.errors)
                online_consultation_form_errors = online_consultation_form.non_form_errors()
                print(online_consultation_form_errors)
                messages.error(request, f"Invalid Details")
                zipped_online_consultation_form = zip(online_consultation_form, WEEK)
                return render(request, "doctor-app/doctor_online_register.html", {
                    'online_consultation_form': zipped_online_consultation_form,
                    'weekdays': WEEK,
                    'online_consultation_form_errors': online_consultation_form_errors,
                    'formset_management_data': online_consultation_form.management_form,
                    })


        zipped_online_consultation_form = zip(online_consultation_form, WEEK)
        return render(request, "doctor-app/doctor_online_register.html", {
            'online_consultation_form': zipped_online_consultation_form,
            'weekdays': WEEK,
            'formset_management_data': online_consultation_form.management_form,
            })



@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorOffDaysRegister(request):
    user = request.user
    doctor_obj = DoctorProfile.objects.get(user=user)
    off_days_form = DoctorOffDaysRegisterForm()

    off_days = DoctorOffDays.objects.filter(doctor=doctor_obj).order_by('-date', '-id')

    paginator = Paginator(off_days, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)


    if request.method == 'POST':
        off_days_form = DoctorOffDaysRegisterForm(request.POST)

        if off_days_form.is_valid():
            form_obj = off_days_form.save(commit=False)
            form_obj.doctor = doctor_obj
            form_obj.save()

            messages.success(request, "Successfully added off days")
            return redirect("doctor_offdays_register")
        else:
            messages.error(request, "Invalid Details")
            return render(request, "doctor-app/doctor_off_days.html", {'off_days_form' : off_days_form, 'page_obj' : page_obj})

    return render(request, "doctor-app/doctor_off_days.html", {'off_days_form' : off_days_form, 'page_obj' : page_obj})



@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorRemoveOffDays(request, day):
    day = get_object_or_404(DoctorOffDays, id=day)
    day.delete()
    messages.success(request, "Successfully removed off day")
    return redirect("doctor_offdays_register")



