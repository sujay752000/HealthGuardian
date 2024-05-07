from django.shortcuts import render, HttpResponse, redirect
from accounts.models import DoctorProfile
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from health_guardian.settings import EMAIL_HOST_USER, CONTACT_EMAIL
from django.contrib.sites.shortcuts import get_current_site


def index_view(request):
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
    paginator = Paginator(filtered_doctors, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    details = {
        "page_obj": page_obj
    }


    if request.method == 'POST':

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email_addr = request.POST.get("email_addr")
        coments = request.POST.get("coments")

        if first_name and last_name and email_addr and coments:
            email = EmailMessage(
                subject="Contact Message",
                body=f"Message = {coments} \nFrom : {first_name} {last_name}\n Email : {email_addr}",
                from_email=EMAIL_HOST_USER,
                to=[CONTACT_EMAIL]
            )
            email.send(fail_silently=True)


            email_2 = EmailMessage(
                subject="Thank you for connecting us !",
                body="Thank you for reaching out and connecting with us! Your message has been received, and our team will respond to you as soon as possible. We appreciate your patience and look forward to assisting you further.",
                from_email=EMAIL_HOST_USER,
                to=[email_addr]
            )

            email_2.send(fail_silently=True)

            if request.is_secure():
                protocol = 'https'
            else:
                protocol = 'http'
                url = protocol + "://" + str(get_current_site(request)) + '#contact_us'

            return redirect(url)
        else:

            if request.is_secure():
                protocol = 'https'
            else:
                protocol = 'http'
                url = protocol + "://" + str(get_current_site(request)) + '#contact_us'

            return redirect(url)

    return render(request, "index.html", context=details)


