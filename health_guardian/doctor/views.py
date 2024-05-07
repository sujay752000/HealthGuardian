from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import is_admin, is_patient, is_doctor
from accounts.models import DoctorProfile
from .forms import ClinicAppointmentTimingsRegisterForm, OnlineConsultationTimingsRegisterForm, ClinicRegisterForm, DoctorOffDaysRegisterForm
from .models import ClinicDetails, ClinicAppointmnetTimings, OnlineConsultationTimings, DoctorOffDays
from django.forms import formset_factory
from .forms import BaseAppointmentFormSet, ClinicAppointmentTimingsUpdateForm, OnlineAppointmentTimingsUpdateForm, DoctorUserUpdateForm, DoctorProfileUpdateForm
from .models import WEEK, ClinicAppointmnetTimings, ClinicDetails, OnlineConsultationTimings, DoctorPredictedDisease
from django.contrib import messages
from django.core.paginator import Paginator
from patient.models import PatientBookedAppointment, PatientProfile, PatientPredictedDisease, OnlineConsultationPassKeys
from django.contrib.sites.shortcuts import get_current_site
from Predict.views import predictDisease
from llm_functionality.views import generateAboutDisease, generate_diet_doctor, generate_precaution_doctor
from django.template.loader import render_to_string
from health_guardian.settings import EMAIL_HOST_USER
from django.core.mail import EmailMessage
# Create your views here.

# pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None


def calculate_bmi(height_cm, weight_kg):
    # Convert height from cm to meters
    height_m = height_cm / 100
    
    # Calculate BMI
    bmi = weight_kg / (height_m ** 2)
    
    # Classify BMI
    if bmi < 16:
        return f"{bmi:.2f}: Severe Thinness"
    elif 16 <= bmi < 17:
        return f"{bmi:.2f}: Moderate Thinness"
    elif 17 <= bmi < 18.5:
        return f"{bmi:.2f}: Mild Thinness"
    elif 18.5 <= bmi < 25:
        return f"{bmi:.2f}: Normal"
    elif 25 <= bmi < 30:
        return f"{bmi:.2f}: Overweight"
    elif 30 <= bmi < 35:
        return f"{bmi:.2f}: Obese Class I"
    elif 35 <= bmi < 40:
        return f"{bmi:.2f}: Obese Class II"
    else:
        return f"{bmi:.2f}: Obese Class III"
    


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
                online_consultation_form_errors = online_consultation_form.non_form_errors()
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


@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorClinicalAppointments(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)
    patient_name = request.GET.get('patient_name')
    if patient_name:
        consultation_list = PatientBookedAppointment.objects.filter(
            doctor=doctor,
            appointment_type=1,
            patient__user__first_name__icontains=patient_name 
        ).order_by('-date', '-id').all()
    else:
        consultation_list = PatientBookedAppointment.objects.filter(
            doctor=doctor,
            appointment_type=1,
        ).order_by('-date', '-id').all()

    paginator = Paginator(consultation_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "doctor-app/doctor_clinic_consultation_table.html", {"page_obj": page_obj})



@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorPatientViewProfile(request, pk):
    patient = get_object_or_404(PatientProfile, id=pk)
    user = patient.patient
    disease = request.GET.get('disease_name')
    if disease:
        patient_disease = PatientPredictedDisease.objects.filter(patient=patient, disease__icontains=disease).order_by('-date', '-id')
    else:
        patient_disease = PatientPredictedDisease.objects.filter(patient=patient).order_by('-date', '-id').all()
        
    paginator = Paginator(patient_disease, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    details = {
        'user': user,
        'patient' : patient,
        'page_obj' : page_obj,
        'bmi' : calculate_bmi(height_cm=patient.height, weight_kg=patient.weight)
    }

    return render(request, "doctor-app/doctor_patient_profile_view.html", context=details)



@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorOnlineAppointments(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)
    patient_name = request.GET.get('patient_name')
    if patient_name:
        consultation_list = PatientBookedAppointment.objects.filter(
            doctor=doctor,
            appointment_type=2,
            patient__user__first_name__icontains=patient_name 
        ).order_by('-date', '-id').all()
    else:
        consultation_list = PatientBookedAppointment.objects.filter(
            doctor=doctor,
            appointment_type=2,
        ).order_by('-date', '-id').all()

    paginator = Paginator(consultation_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "doctor-app/doctor_online_consultation_table.html", {"page_obj": page_obj})


# video call

# @login_required(login_url='doctor_login')
# @user_passes_test(is_doctor)
# @user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
# @user_passes_test(online_consult_completed, login_url="doctor_online_profile")
# def doctorVideoCall(request):
#     name = request.user.get_full_name()
#     return render(request, 'doctor-app/doctor_video_call.html', {'name': name})

@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorOnlineConsultationOptions(request, booking_id, doctor_id, patient_id):
    pass_key_obj = get_object_or_404(OnlineConsultationPassKeys, booking_instance=booking_id, doctor=doctor_id, patient=patient_id )
    if pass_key_obj:
        doctor_name = DoctorProfile.objects.get(id=doctor_id).user.get_full_name()
        patient_name = PatientProfile.objects.get(id=patient_id).patient.get_full_name()
        details = {
            'doctor_name': doctor_name,
            'patient_name': patient_name,
            'booking_id': booking_id,
            'doctor_id': doctor_id,
            'patient_id': patient_id
        }
        return render(request, "doctor-app/doctor_online_consultation_options.html", context=details)
    else:
        return render(request, "doctor-app/doctor_online_consultation_options.html")



@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorVideoCallOption(request, booking_id, doctor_id, patient_id):
    pass_key_obj = get_object_or_404(OnlineConsultationPassKeys, booking_instance=booking_id, doctor=doctor_id, patient=patient_id )
    pass_key = pass_key_obj.pass_key
    if pass_key_obj:
        protocol = 'http'
        if request.is_secure():
            protocol = 'https'
        else:
            protocol = 'http'

        url_join = protocol + "://" + str(get_current_site(request)) + f"/videochat/videocall?roomID={pass_key}&booking_id={booking_id}&doctor_id={doctor_id}&patient_id={patient_id}"

        return redirect(url_join)
        

@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorChatOption(request, booking_id, doctor_id, patient_id):
    pass_key_obj = get_object_or_404(OnlineConsultationPassKeys, booking_instance=booking_id, doctor=doctor_id, patient=patient_id )
    pass_key = pass_key_obj.pass_key
    if pass_key_obj:
        protocol = 'http'
        if request.is_secure():
            protocol = 'https'
        else:
            protocol = 'http'

        # url_join = protocol + "://" + str(get_current_site(request)) + f"/onlinechat/chat?roomID={pass_key}&booking_id={booking_id}&doctor_id={doctor_id}&patient_id={patient_id}"

        return redirect("chat", room=pass_key)
        



@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorJoinCall(request, booking_id, doctor_id, patient_id):
    pass_key_obj = get_object_or_404(OnlineConsultationPassKeys, booking_instance=booking_id, doctor=doctor_id, patient=patient_id )
    pass_key = pass_key_obj.pass_key
    if request.method == 'POST':
        roomID = request.POST['roomID']
        if roomID == pass_key:
            protocol = 'http'
            if request.is_secure():
                protocol = 'https'
            else:
                protocol = 'http'

            messages.success(request, "Please select any mode for consultation:")
            return redirect("doctor_consultation_options", booking_id=booking_id, doctor_id=doctor_id, patient_id=patient_id)

        else:
            messages.error(request, "Invalid Pass Key")
    return render(request, 'doctor-app/doctor_join_video_call.html', {'pass_key': pass_key})




@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorDiseasePredict(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)

    symptoms = ['Itching', 'Skin Rash', 'Nodal Skin Eruptions', 'Continuous Sneezing', 'Shivering', 'Chills', 'Joint Pain', 'Stomach Pain', 'Acidity', 'Ulcers On Tongue', 'Muscle Wasting', 'Vomiting', 'Burning Micturition', 'Fatigue', 'Weight Gain', 'Anxiety', 'Cold Hands And Feets', 'Mood Swings', 'Weight Loss', 'Restlessness', 'Lethargy', 'Patches In Throat', 'Irregular Sugar Level', 'Cough', 'High Fever', 'Sunken Eyes', 'Breathlessness', 'Sweating', 'Dehydration', 'Indigestion', 'Headache', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Loss Of Appetite', 'Pain Behind The Eyes', 'Back Pain', 'Constipation', 'Abdominal Pain', 'Diarrhoea', 'Mild Fever', 'Yellow Urine', 'Yellowing Of Eyes', 'Acute Liver Failure', 'Fluid Overload', 'Swelling Of Stomach', 'Swelled Lymph Nodes', 'Malaise', 'Blurred And Distorted Vision', 'Phlegm', 'Throat Irritation', 'Redness Of Eyes', 'Sinus Pressure', 'Runny Nose', 'Congestion', 'Chest Pain', 'Weakness In Limbs', 'Fast Heart Rate', 'Pain During Bowel Movements', 'Pain In Anal Region', 'Bloody Stool', 'Irritation In Anus', 'Neck Pain', 'Dizziness', 'Cramps', 'Bruising', 'Obesity', 'Swollen Legs', 'Swollen Blood Vessels', 'Puffy Face And Eyes', 'Enlarged Thyroid', 'Brittle Nails', 'Swollen Extremeties', 'Excessive Hunger', 'Extra Marital Contacts', 'Drying And Tingling Lips', 'Slurred Speech', 'Knee Pain', 'Hip Joint Pain', 'Muscle Weakness', 'Stiff Neck', 'Swelling Joints', 'Movement Stiffness', 'Spinning Movements', 'Loss Of Balance', 'Unsteadiness', 'Weakness Of One Body Side', 'Loss Of Smell', 'Bladder Discomfort', 'Foul Smell Of urine', 'Continuous Feel Of Urine', 'Passage Of Gases', 'Internal Itching', 'Toxic Look (typhos)', 'Depression', 'Irritability', 'Muscle Pain', 'Altered Sensorium', 'Red Spots Over Body', 'Belly Pain', 'Abnormal Menstruation',  'Watering From Eyes', 'Increased Appetite', 'Polyuria', 'Family History', 'Mucoid Sputum', 'Rusty Sputum', 'Lack Of Concentration', 'Visual Disturbances', 'Receiving Blood Transfusion', 'Receiving Unsterile Injections', 'Coma', 'Stomach Bleeding', 'Distention Of Abdomen', 'History Of Alcohol Consumption', 'Fluid Overload.1', 'Blood In Sputum', 'Prominent Veins On Calf', 'Palpitations', 'Painful Walking', 'Pus Filled Pimples', 'Blackheads', 'Scurring', 'Skin Peeling', 'Silver Like Dusting', 'Small Dents In Nails', 'Inflammatory Nails', 'Blister', 'Red Sore Around Nose', 'Yellow Crust Ooze']
    context_symptoms = {'my_list': symptoms}
    if request.method == 'POST':
        # Get the list of selected symptoms from the form
        user_symptoms = request.POST.getlist('native-select')

        if user_symptoms[0] == '':
            messages.error(request, "Please Enter your Symptoms")
            return redirect("patient_predict_disease")
        else:
            """ Calling the predicting disease function """
            predicted_disease = predictDisease(user_symptoms[0])

            about_disease = generateAboutDisease(predicted_disease)

            doctor_obj = DoctorPredictedDisease(doctor=doctor, symptoms=user_symptoms[0], model="Disease Prediction Model", disease=predicted_disease )
            doctor_obj.save()

            # Pass the predicted disease to the template context
            context_symptoms = {
                'my_list': symptoms,
                'predicted_disease': predicted_disease,
                'about_disease' : about_disease
            }
            # Pass the symptoms list to the template context

            return render(request, 'doctor-app/doctor_disease_predict.html', context=context_symptoms)
            # return predicted_disease


    # If the request method is not POST, render the form again
    return render(request, 'doctor-app/doctor_disease_predict.html', context=context_symptoms)




@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorDietPrecautionView(request):
    user = request.user
    doctor = DoctorProfile.objects.get(user=user)
    disease = request.GET.get('disease_name')
    if disease:
        doctor_details = DoctorPredictedDisease.objects.filter(doctor=doctor, disease__icontains=disease).order_by('-date', '-id')
    else:
        doctor_details = DoctorPredictedDisease.objects.filter(doctor=doctor).order_by('-date', '-id').all()
        
    paginator = Paginator(doctor_details, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "doctor-app/doctor_diet_precaution.html", {"page_obj": page_obj})

##############################################################################################################


@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorDietChart(request, disease):

    user = request.user
    name = user.get_full_name()
    doctor_email = user.email

    content = generate_diet_doctor(disease=disease)

    pdf = render_to_pdf("patient-app/patient_diet_download.html", {"disease": disease, "content": content})
    if pdf:
        filename = f"{name}_{disease}_diet_chart.pdf"
            
        Subject = f"Diet Chart for {disease}"
        message = render_to_string('doctor-app/doctor_email_llm_content.html', {
            'name' : name,
            'content': "Diet Chart",
            'disease' : disease,
            'domain' : get_current_site(request).domain,
            'protocol': 'https' if request.is_secure() else 'http'
        })
            
        email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[doctor_email])
        email.attach(filename, pdf, 'application/pdf')
        email.content_subtype = 'html' 
        email.send(fail_silently=True)
        messages.success(request, "Diet chart has been sent to your email.")


    return render(request, "doctor-app/doctor_diet.html", {"disease": disease, "content": content })




@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorPrecaution(request, disease):

    user = request.user
    name = user.get_full_name()
    doctor_email = user.email

    content = generate_precaution_doctor(disease=disease)

    pdf = render_to_pdf("patient-app/patient_precaution_download.html", {"disease": disease, "content": content})
    if pdf:
        filename = f"{name}_{disease}_precaution.pdf"
        Subject = f"Precautions for {disease}"
        message = render_to_string('doctor-app/doctor_email_llm_content.html', {
            'name' : name,
            'content': "Precautions",
            'disease' : disease,
            'domain' : get_current_site(request).domain,
            'protocol': 'https' if request.is_secure() else 'http'
            })
            
        email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[doctor_email])
        email.attach(filename, pdf, 'application/pdf')
        email.content_subtype = 'html' 
        email.send(fail_silently=True)
        messages.success(request, "Precautions chart has been sent to your email.")

    return render(request, "doctor-app/doctor_precaution.html", {"disease": disease, "content": content })



############################################################################################################

@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
@user_passes_test(clinic_profile_completed, login_url="doctor_clinic_profile")
@user_passes_test(online_consult_completed, login_url="doctor_online_profile")
def doctorChatAssistant(request):
    protocol = 'http'
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    url_chat_response =  protocol + "://" + str(get_current_site(request)) + f"/llm/chat-response?prompt="
    return render(request, "doctor-app/doctor_chat_assistant.html", {'url_chat_response': url_chat_response})



