from django.shortcuts import render, HttpResponse
from accounts.models import DoctorProfile
from django.db.models import Q
from django.core.paginator import Paginator


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
    print(specialization, state, district)
    print(doctors)
    paginator = Paginator(filtered_doctors, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "index.html", {"page_obj": page_obj})

