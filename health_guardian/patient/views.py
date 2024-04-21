from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import is_admin, is_patient, is_doctor
from accounts.forms import UserRegisterationForm
from .forms import PatientProfileForm, PatientUpdateProfileForm, PatientUserUpdateForm
from .models import PatientProfile, PatientPredictedDisease
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



from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os

# Create your views here.

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
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
    doctor = DoctorProfile.objects.get(id=doctor)
    clinic = ClinicDetails.objects.get(doctor=doctor)
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
        'clinic_start_time' : clinic_start_time,
        'clinic_end_time': clinic_end_time,
        'online_start_time' : online_start_time,
        'online_end_time': online_end_time,
        'off_day': off_day
    }

    return render(request, "patient-app/patient_book_appointment_view.html", context=details)


