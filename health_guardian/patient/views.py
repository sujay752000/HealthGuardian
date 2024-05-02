from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import is_admin, is_patient, is_doctor
from accounts.forms import UserRegisterationForm
from .forms import PatientProfileForm, PatientUpdateProfileForm, PatientUserUpdateForm
from .models import PatientProfile, PatientPredictedDisease, PatientBookedAppointment, OnlineConsultationPassKeys
from llm_functionality.views import generateHealthTip, generateAboutDisease, generate_diet, generate_precaution
from doctor.models import DoctorProfile, ClinicAppointmnetTimings, ClinicDetails, OnlineConsultationTimings, DoctorOffDays
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count
from Predict.views import predictDisease
from django.core.mail import EmailMessage
from health_guardian.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from datetime import date
import datetime
import calendar
from django.utils import timezone
import json
import razorpay
from django.views.decorators.csrf import csrf_exempt
import random
import string


# pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os

# Razorpay
from health_guardian.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

# Pass Key Generator
def generate_passkey():
    num_count = 3
    passkey = ''.join(random.choices(string.ascii_letters, k=3) + random.choices(string.digits, k=num_count))
    passkey += ''.join(random.choices(string.ascii_letters + string.digits, k=3 - num_count))
    passkey_list = list(passkey)
    random.shuffle(passkey_list)
    return ''.join(passkey_list)


# Create your views here.

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None


def render_to_pdf_2(html_content):
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None


def profile_completed(user):
    patient = PatientProfile.objects.filter(patient=user)
    if patient:
        return True

def profile_not_completed(user):
    patient = PatientProfile.objects.filter(patient=user)
    if not patient:
        return True


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
    


@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientDashboard(request):
    user = request.user
    patient = PatientProfile.objects.get(patient=user)
    bmi = calculate_bmi(height_cm=patient.height, weight_kg=patient.weight)
    health_tip = generateHealthTip()
    return render(request, 'patient-app/patient_dashboard.html', {'user': user, 'patient': patient, 'bmi': bmi, 'tip': health_tip})


@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientDiseasePredict(request):
    user = request.user
    patient = PatientProfile.objects.get(patient=user)

    symptoms = ['Itching', 'Skin Rash', 'Nodal Skin Eruptions', 'Continuous Sneezing', 'Shivering', 'Chills', 'Joint Pain', 'Stomach Pain', 'Acidity', 'Ulcers On Tongue', 'Muscle Wasting', 'Vomiting', 'Burning Micturition', 'Fatigue', 'Weight Gain', 'Anxiety', 'Cold Hands And Feets', 'Mood Swings', 'Weight Loss', 'Restlessness', 'Lethargy', 'Patches In Throat', 'Irregular Sugar Level', 'Cough', 'High Fever', 'Sunken Eyes', 'Breathlessness', 'Sweating', 'Dehydration', 'Indigestion', 'Headache', 'Yellowish Skin', 'Dark Urine', 'Nausea', 'Loss Of Appetite', 'Pain Behind The Eyes', 'Back Pain', 'Constipation', 'Abdominal Pain', 'Diarrhoea', 'Mild Fever', 'Yellow Urine', 'Yellowing Of Eyes', 'Acute Liver Failure', 'Fluid Overload', 'Swelling Of Stomach', 'Swelled Lymph Nodes', 'Malaise', 'Blurred And Distorted Vision', 'Phlegm', 'Throat Irritation', 'Redness Of Eyes', 'Sinus Pressure', 'Runny Nose', 'Congestion', 'Chest Pain', 'Weakness In Limbs', 'Fast Heart Rate', 'Pain During Bowel Movements', 'Pain In Anal Region', 'Bloody Stool', 'Irritation In Anus', 'Neck Pain', 'Dizziness', 'Cramps', 'Bruising', 'Obesity', 'Swollen Legs', 'Swollen Blood Vessels', 'Puffy Face And Eyes', 'Enlarged Thyroid', 'Brittle Nails', 'Swollen Extremeties', 'Excessive Hunger', 'Extra Marital Contacts', 'Drying And Tingling Lips', 'Slurred Speech', 'Knee Pain', 'Hip Joint Pain', 'Muscle Weakness', 'Stiff Neck', 'Swelling Joints', 'Movement Stiffness', 'Spinning Movements', 'Loss Of Balance', 'Unsteadiness', 'Weakness Of One Body Side', 'Loss Of Smell', 'Bladder Discomfort', 'Foul Smell Of urine', 'Continuous Feel Of Urine', 'Passage Of Gases', 'Internal Itching', 'Toxic Look (typhos)', 'Depression', 'Irritability', 'Muscle Pain', 'Altered Sensorium', 'Red Spots Over Body', 'Belly Pain', 'Abnormal Menstruation',  'Watering From Eyes', 'Increased Appetite', 'Polyuria', 'Family History', 'Mucoid Sputum', 'Rusty Sputum', 'Lack Of Concentration', 'Visual Disturbances', 'Receiving Blood Transfusion', 'Receiving Unsterile Injections', 'Coma', 'Stomach Bleeding', 'Distention Of Abdomen', 'History Of Alcohol Consumption', 'Fluid Overload.1', 'Blood In Sputum', 'Prominent Veins On Calf', 'Palpitations', 'Painful Walking', 'Pus Filled Pimples', 'Blackheads', 'Scurring', 'Skin Peeling', 'Silver Like Dusting', 'Small Dents In Nails', 'Inflammatory Nails', 'Blister', 'Red Sore Around Nose', 'Yellow Crust Ooze']
    context_symptoms = {'my_list': symptoms}
    if request.method == 'POST':
        # Get the list of selected symptoms from the form
        user_symptoms = request.POST.getlist('native-select')

        if user_symptoms[0] == '':
            messages.error(request, "Please Enter your Symptoms")
            return redirect("patient_predict_disease")
        else:
            print(user_symptoms[0])
            """ Calling the predicting disease function """
            predicted_disease = predictDisease(user_symptoms[0])

            about_disease = generateAboutDisease(predicted_disease)

            patient_obj = PatientPredictedDisease(patient=patient, symptoms=user_symptoms[0], model="Disease Prediction Model", disease=predicted_disease )
            patient_obj.save()

            # Pass the predicted disease to the template context
            context_symptoms = {
                'my_list': symptoms,
                'predicted_disease': predicted_disease,
                'about_disease' : about_disease
            }
            # Pass the symptoms list to the template context

            return render(request, 'patient-app/patient_disease_predict.html', context=context_symptoms)
            # return predicted_disease


    # If the request method is not POST, render the form again
    return render(request, 'patient-app/patient_disease_predict.html', context=context_symptoms)





@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_not_completed, login_url="patient_dashboard")
def patientProfileRegister(request):
    user = request.user
    form = PatientProfileForm()
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.patient = user
            profile.save()
            return redirect("patient_dashboard")
        else:
            messages.error(request, "Please enter your details correctly")
            return render(request, 'patient-app/patient_profile.html', {'form': form})

    return render(request, 'patient-app/patient_profile.html', {'form': form})



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientProfileUpdate(request):
    user = request.user
    patient = PatientProfile.objects.get(patient=user)

    user_form = PatientUserUpdateForm(instance = user)
    patient_form = PatientUpdateProfileForm(instance = patient)

    if request.method == 'POST':
        user_form = PatientUserUpdateForm(request.POST, instance=user)
        patient_form = PatientUpdateProfileForm(request.POST, request.FILES, instance=patient)
        patient_photo = request.POST.get("photo")
        if user_form.is_valid() and patient_form.is_valid():
            user_form.save()
            if patient_photo:
                patient_form.photo = patient_photo
                patient_form.save()
            patient_form.save()
            messages.success(request, "Successfully updated your profile")
            return redirect("patient_update")
        else:
            messages.error(request, "Invalid details")
            return render(request, 'patient-app/patient_view.html', {'patient': patient,'user_form': user_form, 'patient_form': patient_form})
    
    return render(request, 'patient-app/patient_view.html', {'patient': patient,'user_form': user_form, 'patient_form': patient_form})



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientSearchDoctors(request):
    specialization = request.GET.get('doctor_specialization')
    state = request.GET.get('doctor_state')
    district = request.GET.get('doctor_district')

    # Fetch all doctors who are approved
    doctors = DoctorProfile.objects.filter(admin_approved=True)

    # If no search parameters are provided, filter doctors by distinct specializations
    if not any([specialization, state, district]):
        distinct_specializations = doctors.order_by('specialization').values_list('specialization', flat=True).distinct()
        filtered_doctors = DoctorProfile.objects.filter(admin_approved=True, specialization__in=distinct_specializations)
    else:
        # Otherwise, apply filters based on the provided parameters
        if specialization:
            doctors = doctors.filter(specialization__icontains=specialization)

        if state or district:
            clinic_details_filter = Q()
            if state:
                clinic_details_filter &= Q(clinicdetails__state__icontains=state)
            if district:
                clinic_details_filter &= Q(clinicdetails__district__icontains=district)
            # Filter doctors based on ClinicDetails
            doctors = doctors.filter(clinicdetails__isnull=False).filter(clinic_details_filter)
        filtered_doctors = doctors

    # Paginate the filtered queryset
    paginator = Paginator(filtered_doctors, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "patient-app/patient_doctor_search.html", {"page_obj": page_obj})



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientDoctorProfileView(request, pk):
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

    return render(request, "patient-app/patient_doctor_profile_view.html", context=details)



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientDietPrecautionView(request):
    user = request.user
    patient = PatientProfile.objects.get(patient=user)
    disease = request.GET.get('disease_name')
    if disease:
        patient_details = PatientPredictedDisease.objects.filter(patient=patient, disease__icontains=disease).order_by('-date', '-id')
    else:
        patient_details = PatientPredictedDisease.objects.filter(patient=patient).order_by('-date', '-id').all()
        
    paginator = Paginator(patient_details, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "patient-app/patient_diet_precaution.html", {"page_obj": page_obj})



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientDietChart(request, disease):

    user = request.user
    name = user.get_full_name()
    patient_email = user.email
    patient = PatientProfile.objects.get(patient=user)

    chronic_disease = ",".join(patient.chronic_diseases.split())

    bmi = calculate_bmi(height_cm=patient.height, weight_kg=patient.weight)

    content = generate_diet(disease=disease, chronic_disease=chronic_disease, bmi=bmi)

    pdf = render_to_pdf("patient-app/patient_diet_download.html", {"disease": disease, "content": content})
    if pdf:
        filename = f"{name}_{disease}_diet_chart.pdf"
            
        Subject = f"Diet Chart for {disease}"
        message = render_to_string('patient-app/patient_email_llm_content.html', {
            'name' : name,
            'content': "Diet Chart",
            'disease' : disease,
            'domain' : get_current_site(request).domain,
            'protocol': 'https' if request.is_secure() else 'http'
            })
            
        email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[patient_email])
        email.attach(filename, pdf, 'application/pdf')
        email.content_subtype = 'html' 
        email.send(fail_silently=True)
        messages.success(request, "Diet chart has been sent to your email.")


    return render(request, "patient-app/patient_diet.html", {"disease": disease, "content": content })




@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientPrecaution(request, disease):

    user = request.user
    name = user.get_full_name()
    patient_email = user.email
    patient = PatientProfile.objects.get(patient=user)

    chronic_disease = ",".join(patient.chronic_diseases.split())

    bmi = calculate_bmi(height_cm=patient.height, weight_kg=patient.weight)

    content = generate_precaution(disease=disease, chronic_disease=chronic_disease, bmi=bmi)

    pdf = render_to_pdf("patient-app/patient_precaution_download.html", {"disease": disease, "content": content})
    if pdf:
        filename = f"{name}_{disease}_precaution.pdf"
        Subject = f"Precautions for {disease}"
        message = render_to_string('patient-app/patient_email_llm_content.html', {
            'name' : name,
            'content': "Precautions",
            'disease' : disease,
            'domain' : get_current_site(request).domain,
            'protocol': 'https' if request.is_secure() else 'http'
            })
            
        email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[patient_email])
        email.attach(filename, pdf, 'application/pdf')
        email.content_subtype = 'html' 
        email.send(fail_silently=True)
        messages.success(request, "Precautions chart has been sent to your email.")

    return render(request, "patient-app/patient_precaution.html", {"disease": disease, "content": content })


@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientBookAppointmentView(request, doctor):
    user = request.user
    patient = PatientProfile.objects.get(patient=user)

    doctor = DoctorProfile.objects.get(id=doctor)
    date_today = date.today()

    off_day = DoctorOffDays.objects.filter(date=date_today)

    current_day = date_today.strftime("%A").lower()

    clinic_timings = ClinicAppointmnetTimings.objects.get(doctor=doctor, day=current_day)
    clinic_start_time = clinic_timings.start_time
    clinic_end_time = clinic_timings.end_time

    online_timings = OnlineConsultationTimings.objects.get(doctor=doctor, day=current_day)
    online_start_time = online_timings.start_time
    online_end_time = online_timings.end_time


    details = {
        'date' : date_today,
        'doctor' : doctor.id,
        'patient' : patient.id,
        'doctor_name': doctor.user.get_full_name(),
        'clinic_start_time' : clinic_start_time,
        'clinic_end_time': clinic_end_time,
        'online_start_time' : online_start_time,
        'online_end_time': online_end_time,
        'off_day': off_day
    }

    return render(request, "patient-app/patient_book_appointment_view.html", context=details)



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientClinicBookAppointmeentDate(request, doctor_id, patient_id):

    doctor = DoctorProfile.objects.get(id=doctor_id)
    patient = PatientProfile.objects.get(id=patient_id)

    clinic = ClinicDetails.objects.get(doctor=doctor)
    clinic_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor)

    off_days = DoctorOffDays.objects.filter(doctor=doctor).values_list('date', flat=True)
    formatted_off_days = [date.strftime('%Y-%m-%d') for date in off_days]

    # Fetch weekdays without start or end times
    weekdays_without_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor, start_time__isnull=True).values_list('day', flat=True)

    # Capitalize the weekdays
    formatted_weekdays_without_timings = [day.capitalize() for day in weekdays_without_timings]

    details = {
        'doctor': doctor,
        'clinic': clinic,
        'clinic_timings': clinic_timings,
        'off_days': json.dumps(formatted_off_days),
        'weekdays_without_timings':  json.dumps(formatted_weekdays_without_timings)
    }

    if request.method == 'POST':
        user_date = request.POST.get('booked_date')
        user_date = datetime.datetime.strptime(user_date, '%m/%d/%Y').date() 

        print(user_date)
        print(user_date.strftime('%Y-%m-%d'))
        print(user_date.strftime('%A'))

        if user_date not in formatted_off_days and calendar.day_name[user_date.weekday()].capitalize() not in formatted_weekdays_without_timings:
            messages.success(request, f"Selected date {user_date}, please select your comfortable time slot")
            return redirect("patient_clinic_appointment_time", doctor_id=doctor_id, patient_id=patient_id, date=user_date)
        else:
            messages.error(request, "Inavlid details")
            return render(request, "patient-app/patient_clinic_appointment.html", context=details)

    return render(request, "patient-app/patient_clinic_appointment.html", context=details)




@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientOnlineBookAppointmeentDate(request, doctor_id, patient_id):

    doctor = DoctorProfile.objects.get(id=doctor_id)
    patient = PatientProfile.objects.get(id=patient_id)

    online_timings = OnlineConsultationTimings.objects.filter(doctor=doctor)

    off_days = DoctorOffDays.objects.filter(doctor=doctor).values_list('date', flat=True)
    formatted_off_days = [date.strftime('%Y-%m-%d') for date in off_days]

    # Fetch weekdays without start or end times
    weekdays_without_timings = OnlineConsultationTimings.objects.filter(doctor=doctor, start_time__isnull=True).values_list('day', flat=True)

    # Capitalize the weekdays
    formatted_weekdays_without_timings = [day.capitalize() for day in weekdays_without_timings]

    details = {
        'doctor': doctor,
        'online_timings': online_timings,
        'off_days': json.dumps(formatted_off_days),
        'weekdays_without_timings':  json.dumps(formatted_weekdays_without_timings)
    }

    if request.method == 'POST':
        user_date = request.POST.get('booked_date')
        user_date = datetime.datetime.strptime(user_date, '%m/%d/%Y').date() 

        print(user_date)
        print(user_date.strftime('%Y-%m-%d'))
        print(user_date.strftime('%A'))

        print(formatted_off_days)
        print(formatted_weekdays_without_timings)

        if user_date not in formatted_off_days and calendar.day_name[user_date.weekday()].capitalize() not in formatted_weekdays_without_timings:
            print("True")
            messages.success(request, f"Selected date {user_date}, please select your comfortable time slot")
            return redirect("patient_online_appointment_time", doctor_id=doctor_id, patient_id=patient_id, date=user_date)
        else:
            messages.error(request, "Inavlid details")
            return render(request, "patient-app/patient_online_appointment.html", context=details)

    return render(request, "patient-app/patient_online_appointment.html", context=details)




razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
print(razorpay_client)


@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientClinicBookAppointmentTime(request, doctor_id, patient_id, date):
    try:
        user = request.user
        doctor = DoctorProfile.objects.get(id=doctor_id)
        patient = PatientProfile.objects.get(id=patient_id)
        user_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        print(user_date)
        clinic_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor)
        clinic = ClinicDetails.objects.get(doctor=doctor)
        doctor_consulting_fee = clinic.consultation_fee
        off_days = DoctorOffDays.objects.filter(doctor=doctor).values_list('date', flat=True)
        formatted_off_days = [date.strftime('%Y-%m-%d') for date in off_days]

        weekdays_without_timings = ClinicAppointmnetTimings.objects.filter(doctor=doctor, start_time__isnull=True).values_list('day', flat=True)
        formatted_weekdays_without_timings = [day.capitalize() for day in weekdays_without_timings]

        current_date = datetime.date.today()
        print(formatted_off_days)
        print(formatted_weekdays_without_timings)
        print(user_date >= current_date)

        if user_date not in formatted_off_days and calendar.day_name[user_date.weekday()].capitalize() not in formatted_weekdays_without_timings and user_date >= current_date:
            # Get the day of the week from the user_date
            user_day = calendar.day_name[user_date.weekday()]

            # Get clinic timings for the user_day
            clinic_timings_day = clinic_timings.filter(day=user_day.lower())

            # Calculate time slots
            # Calculate time slots
            time_slots = []
            for timing in clinic_timings_day:
                if user_date == current_date:
                    now = datetime.datetime.now().time()
                    start_time = max(timing.start_time, now)
                else:
                    start_time = timing.start_time

                end_time = timing.end_time
                current_time = datetime.datetime.combine(datetime.datetime.now().date(), start_time)

                while current_time.time() < end_time:
                    time_slots.append(current_time.time().strftime('%I:%M %p'))
                    current_time += datetime.timedelta(hours=1)

            print(time_slots)

            if time_slots:

                details = {
                    'user': user,
                    'date': user_date,
                    'day': user_day,
                    'doctor': doctor,
                    'clinic': clinic,
                    'time_slots': time_slots,
                    'clinic_timings': clinic_timings,
                }

                if request.method == 'POST':
                    user_time = request.POST.get('time_booked')

                    if user_time:
                        time = datetime.datetime.now()
                        booking_obj = PatientBookedAppointment(doctor=doctor, patient=patient, appointment_type=1, date=user_date, time=user_time, consulting_fee=doctor_consulting_fee)
                        booking_id = f"BOOKBY{user.id}-{doctor.id}-{time.strftime('%H:%M:%S')}"
                        booking_obj.booking_id = booking_id
                        booking_obj.save()

                        order_currency = 'INR'

                        protocol = 'http'

                        if request.is_secure():
                            protocol = 'https'
                        else:
                            protocol = 'http'

                        callback_url = protocol + "://" + str(get_current_site(request))+"/patient/patient-payment-handler"
                        print(callback_url)

                        print(callback_url)
                        notes = {'order-type': "Consultation Fee"}
                        try:
                            razorpay_order = razorpay_client.order.create(dict(amount=doctor_consulting_fee*100, currency=order_currency, notes = notes, payment_capture='0'))
                            print(razorpay_order['id'])
                            booking_obj.razorpay_order_id = razorpay_order['id']
                            booking_obj.save()

                            details2 = {
                                'time_slot': user_time,
                                'order_id': razorpay_order['id'],
                                'orderId':booking_obj.booking_id,
                                'final_price':doctor_consulting_fee * 100,
                                'razorpay_merchant_id':RAZORPAY_KEY_ID,
                                'callback_url':callback_url
                            }

                            details.update(details2)

                            messages.success(request, "Please confirm your appointment")
                            return render(request, "patient-app/patient_appointment_confirm.html", context=details )
                        
                        except Exception as e:
                            print("Razorpay Error:", e)
                            return HttpResponse("Razorpay Error: " + str(e))
                            
                    else:
                        messages.error(request, "Please Select any time slot")
                        return render(request, "patient-app/patient_clinic_appointment_time.html", context=details)


                return render(request, "patient-app/patient_clinic_appointment_time.html", context=details)
            else:
                messages.error(request, f"No time slotes are available for {user_date} ")
                return redirect("patient_clinic_appointment_date", doctor_id=doctor_id, patient_id=patient_id)
        else:
            messages.error(request, "Invalid Booking Details")
            return redirect("patient_doctor_search")
    except:
        messages.error(request, "Invalid Booking Details")
        return redirect("patient_doctor_search")



###########################################################################################################
################################################# Online Appointmnet ######################################### 
###########################################################################################################


razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientOnlineBookAppointmentTime(request, doctor_id, patient_id, date):
    try:
        user = request.user
        doctor = DoctorProfile.objects.get(id=doctor_id)
        patient = PatientProfile.objects.get(id=patient_id)
        user_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        online_timings = OnlineConsultationTimings.objects.filter(doctor=doctor)
        clinic = ClinicDetails.objects.get(doctor=doctor)
        doctor_consulting_fee = clinic.consultation_fee
        off_days = DoctorOffDays.objects.filter(doctor=doctor).values_list('date', flat=True)
        formatted_off_days = [date.strftime('%Y-%m-%d') for date in off_days]

        weekdays_without_timings = OnlineConsultationTimings.objects.filter(doctor=doctor, start_time__isnull=True).values_list('day', flat=True)
        formatted_weekdays_without_timings = [day.capitalize() for day in weekdays_without_timings]

        current_date = datetime.date.today()

        if user_date not in formatted_off_days and calendar.day_name[user_date.weekday()].capitalize() not in formatted_weekdays_without_timings and user_date >= current_date:
            # Get the day of the week from the user_date
            user_day = calendar.day_name[user_date.weekday()]

            # Get clinic timings for the user_day
            online_timings_day = online_timings.filter(day=user_day.lower())

            # Calculate time slots
            # Calculate time slots
            time_slots = []
            for timing in online_timings_day:
                if user_date == current_date:
                    now = datetime.datetime.now().time()
                    start_time = max(timing.start_time, now)
                else:
                    start_time = timing.start_time

                end_time = timing.end_time
                current_time = datetime.datetime.combine(datetime.datetime.now().date(), start_time)

                while current_time.time() < end_time:
                    time_slots.append(current_time.time().strftime('%I:%M %p'))
                    current_time += datetime.timedelta(hours=1)

            print(time_slots)

            if time_slots:

                details = {
                    'user': user,
                    'date': user_date,
                    'day': user_day,
                    'doctor': doctor,
                    'clinic': clinic,
                    'time_slots': time_slots,
                    'online_timings': online_timings,
                }

                if request.method == 'POST':
                    user_time = request.POST.get('time_booked')

                    if user_time:
                        time = datetime.datetime.now()
                        booking_obj = PatientBookedAppointment(doctor=doctor, patient=patient, appointment_type=2, date=user_date, time=user_time, consulting_fee=doctor_consulting_fee)
                        booking_id = f"BOOKBY{user.id}-{doctor.id}-{time.strftime('%H:%M:%S')}"
                        booking_obj.booking_id = booking_id
                        booking_obj.save()

                        order_currency = 'INR'

                        protocol = 'http'

                        if request.is_secure():
                            protocol = 'https'
                        else:
                            protocol = 'http'

                        callback_url = protocol + "://" + str(get_current_site(request))+"/patient/patient-payment-handler"
                        # callback_url = 'http://'+ str(get_current_site(request))
                        print(callback_url)
                        notes = {'order-type': "Consultation Fee"}
                        try:
                            razorpay_order = razorpay_client.order.create(dict(amount=doctor_consulting_fee*100, currency=order_currency, notes = notes, payment_capture='0'))
                            print(razorpay_order['id'])
                            booking_obj.razorpay_order_id = razorpay_order['id']
                            booking_obj.save()

                            pass_key = generate_passkey()
                            online_pass_key_obj = OnlineConsultationPassKeys(booking_instance=booking_obj, doctor=booking_obj.doctor, patient=booking_obj.patient, pass_key=pass_key)
                            online_pass_key_obj.save()

                            details2 = {
                                'time_slot': user_time,
                                'order_id': razorpay_order['id'],
                                'orderId':booking_obj.booking_id,
                                'final_price':doctor_consulting_fee * 100,
                                'razorpay_merchant_id':RAZORPAY_KEY_ID,
                                'callback_url':callback_url
                            }

                            details.update(details2)

                            messages.success(request, "Please confirm your appointment")
                            return render(request, "patient-app/patient_appointment_confirm.html", context=details )
                        
                        except Exception as e:
                            print("Razorpay Error:", e)
                            return HttpResponse("Razorpay Error: " + str(e))
                            
                    else:
                        messages.error(request, "Please Select any time slot")
                        return render(request, "patient-app/patient_online_appointment_time.html", context=details)


                return render(request, "patient-app/patient_online_appointment_time.html", context=details)
            else:
                messages.error(request, f"No time slotes are available for {user_date} ")
                return redirect("patient_online_appointment_date", doctor_id=doctor_id, patient_id=patient_id)
        else:
            messages.error(request, "Invalid Booking Details")
            return redirect("patient_doctor_search")
    except:
        messages.error(request, "Invalid Booking Details")
        return redirect("patient_doctor_search")




###########################################################################################################
razorpay_client_2 = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
@csrf_exempt
def patientPaymentHandleRequest(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id','')
            signature = request.POST.get('razorpay_signature','')
            params_dict = {
                'razorpay_order_id': order_id, 
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            try:
                booking_db = PatientBookedAppointment.objects.get(razorpay_order_id=order_id)
            except:
                return HttpResponse("505 Not Found")
            
            booking_db.razorpay_payment_id = payment_id
            booking_db.razorpay_signature = signature
            booking_db.save()
            result = razorpay_client_2.utility.verify_payment_signature(params_dict)
            print(result)
            if result==True:
                amount = booking_db.consulting_fee * 100   #we have to pass in paisa
                try:
                    razorpay_client_2.payment.capture(payment_id, amount)
                    booking_db.payment_status = 1
                    booking_db.save()

                    data = {
                        'booking_id': booking_db.booking_id,
                        'transaction_id': booking_db.razorpay_payment_id,
                        'date': str(booking_db.date),
                        'time': str(booking_db.time),
                        'doctor_name': booking_db.doctor.user.get_full_name(),
                        'patient_name': booking_db.patient.patient.get_full_name(),
                        'amount': booking_db.consulting_fee,
                        'domain' : get_current_site(request).domain,
                        'protocol': 'https' if request.is_secure() else 'http',
                    }

                    pass_key = ""

                    if booking_db.appointment_type == 2:
                        pass_key_obj = OnlineConsultationPassKeys.objects.get(booking_instance=booking_db)
                        pass_key = pass_key_obj.pass_key
                        data.update({'pass_key' : pass_key})


                    html_content = render_to_string("patient-app/patient_appointment_success_receipt_email.html", data)

                    pdf = render_to_pdf("patient-app/patient_appointment_receipt.html", data)

                    print("Done-1")

                    if pdf:
                        patient_email = booking_db.patient.patient.email
                        filename = f"Invoice_{booking_db.booking_id}.pdf"
                        Subject = f"Appointment Receipt - Booking id : {booking_db.booking_id}"
                        message = html_content
                        email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[patient_email])
                        email.attach(filename, pdf, 'application/pdf')
                        email.content_subtype = 'html' 
                        email.send(fail_silently=True)
                        print("Done-2")

                    messages.success(request, "Payment successfull appointment receipt has been sent to your email.")
                    print("Done-3")
                    if booking_db.appointment_type == 1:
                        return redirect("patient_clinic_consultations")
                    else:
                        return redirect("patient_online_consultations")
                        

                except Exception as e:
                    booking_db.payment_status = 2
                    booking_db.save()

                    patient_email = booking_db.patient.patient.email
                    Subject = f"Appointment Booking Failed !"
                    data = {
                        'patient_name': booking_db.patient.patient.get_full_name(),
                        'domain' : get_current_site(request).domain,
                        'protocol': 'https' if request.is_secure() else 'http'
                    }
                    message = render_to_string("patient-app/patient_appointment_fail_email.html", context=data)
                    email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[patient_email])
                    email.content_subtype = 'html' 
                    email.send(fail_silently=True)

                    booking_db.delete()
                    messages.error(request, "Payment failed try booking again.")
                    return redirect("patient_doctor_search")
            else:
                booking_db.payment_status = 2
                booking_db.save()

                patient_email = booking_db.patient.patient.email
                Subject = f"Appointment Booking Failed !"
                data = {
                    'patient_name': booking_db.patient.patient.get_full_name(),
                    'domain' : get_current_site(request).domain,
                    'protocol': 'https' if request.is_secure() else 'http'
                }
                message = render_to_string("patient-app/patient_appointment_fail_email.html", context=data)
                email = EmailMessage(subject=Subject, body=message, from_email=EMAIL_HOST_USER, to=[patient_email])
                email.content_subtype = 'html' 
                email.send(fail_silently=True)

                booking_db.delete()

                messages.error(request, "Payment failed try booking again.")
                return redirect("patient_doctor_search")
            
        except:
            messages.error(request, "Payment failed try booking again.")
            return redirect("patient_doctor_search")



###################################################################################################################


@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientOnlineConsultationTable(request):
    user = request.user
    patient = PatientProfile.objects.get(patient=user)
    doctor_name = request.GET.get('doctor_name')
    if doctor_name:
        consultation_list = PatientBookedAppointment.objects.filter(
            patient=patient,
            appointment_type=2,
            payment_status=1,
            doctor__user__first_name__icontains=doctor_name  # Corrected filtering
        ).order_by('-date', '-id').all()
    else:
        consultation_list = PatientBookedAppointment.objects.filter(
            patient=patient,
            appointment_type=2,
            payment_status=1,
        ).order_by('-date', '-id').all()

    paginator = Paginator(consultation_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "patient-app/patient_consultation_table.html", {"page_obj": page_obj})


###########################################################################################################

@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientClinicConsultationTable(request):
    user = request.user
    patient = PatientProfile.objects.get(patient=user)
    doctor_name = request.GET.get('doctor_name')
    if doctor_name:
        consultation_list = PatientBookedAppointment.objects.filter(
            patient=patient,
            appointment_type=1,
            payment_status=1,
            doctor__user__first_name__icontains=doctor_name 
        ).order_by('-date', '-id').all()
    else:
        consultation_list = PatientBookedAppointment.objects.filter(
            patient=patient,
            appointment_type=1,
            payment_status=1,
        ).order_by('-date', '-id').all()

    paginator = Paginator(consultation_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "patient-app/patient_clinic_consultation_table.html", {"page_obj": page_obj})



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientVideoCallView(request):
    return render(request, "patient-app/patient_video_call_view.html")




@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientVideoCall(request):
    name = request.user.get_full_name()
    return render(request, 'patient-app/patient_video_call.html', {'name': name})



@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientJoinCall(request, booking_id, doctor_id, patient_id):
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

            url_join = protocol + "://" + str(get_current_site(request)) + f"/videochat/videocall?roomID={roomID}&booking_id={booking_id}&doctor_id={doctor_id}&patient_id={patient_id}"

            return redirect(url_join)
        else:
            messages.error(request, "Invalid Pass Key")
    return render(request, 'patient-app/patient_join_video_call.html', {'pass_key': pass_key})




@login_required(login_url='patient_login')
@user_passes_test(is_patient)
@user_passes_test(profile_completed, login_url="patient_profile")
def patientChatAssistant(request):
    protocol = 'http'
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    url_chat_response =  protocol + "://" + str(get_current_site(request)) + f"/llm/chat-response?prompt="
    return render(request, "patient-app/patient_chat_assistant.html", {'url_chat_response': url_chat_response})




