from django.contrib.auth.models import User, Group
from accounts.models import DoctorProfile, SPECIALIZATIONS
from doctor.models import ClinicDetails, ClinicAppointmnetTimings, OnlineConsultationTimings
from faker import Faker
from random import sample
from datetime import time


# Define the number of doctors to add for each specialization
num_doctors_per_specialization = 5

# Initialize Faker to generate random names
fake = Faker()

# List to store generated first names
used_first_names = []

# Weekdays
WEEK = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday')
]

# List of Kerala districts
KERALA_DISTRICTS = [
    'Alappuzha', 'Ernakulam', 'Idukki', 'Kannur', 'Kasaragod',
    'Kollam', 'Kottayam', 'Kozhikode', 'Malappuram', 'Palakkad',
    'Pathanamthitta', 'Thiruvananthapuram', 'Thrissur', 'Wayanad'
]

# Iterate over each specialization
for specialization_key, specialization_value in SPECIALIZATIONS:
    users_for_specialization = []
    for i in range(num_doctors_per_specialization):
        # Generate a unique first name
        while True:
            first_name = fake.first_name()
            if first_name not in used_first_names:
                used_first_names.append(first_name)
                break
        
        last_name = fake.last_name()

        username = f"{first_name.lower()}@doctor"
        email = "sujayprasad010@gmail.com"
        password = "amma@123"
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        
        group = Group.objects.get_or_create(name='doctor')
        group[0].user_set.add(user)

        users_for_specialization.append(user)

        # Create DoctorProfile
        experience = (i * 2) + 1 
        doctor_profile = DoctorProfile.objects.create(
            user=user,
            specialization=specialization_value,
            experiance=experience,
            admin_approved=True
        )

        # Create ClinicDetails
        clinic_name = f"{first_name}'s Clinic"
        consultation_fee = 100
        state = "Kerala"
        district = KERALA_DISTRICTS[i % len(KERALA_DISTRICTS)]  # Cycle through Kerala districts
        clinic_details = ClinicDetails.objects.create(
            doctor=doctor_profile,
            clinic_name=clinic_name,
            consultation_fee=consultation_fee,
            state=state,
            district=district
        )

        # Create ClinicAppointmentTimings
        for day, weekday in WEEK:
            start_time = time(hour=9, minute=0)  # Default start time
            end_time = time(hour=16, minute=0)   # Default end time
            if weekday not in ['Saturday', 'Sunday']:  # Exclude weekends
                ClinicAppointmnetTimings.objects.create(
                    doctor=doctor_profile,
                    day=day,
                    start_time=start_time,
                    end_time=end_time
                )
            else:  # Set blank start_time and end_time for Saturday and Sunday
                ClinicAppointmnetTimings.objects.create(
                    doctor=doctor_profile,
                    day=day,
                    start_time="",
                    end_time=""
                )

        # Create OnlineConsultationTimings
        for day, weekday in WEEK:
            start_time = time(hour=16, minute=0)  # Default start time
            end_time = time(hour=21, minute=0)    # Default end time
            if weekday not in ['Saturday', 'Sunday']:  # Exclude weekends
                OnlineConsultationTimings.objects.create(
                    doctor=doctor_profile,
                    day=day,
                    start_time=start_time,
                    end_time=end_time
                )
            else:  # Set blank start_time and end_time for Saturday and Sunday
                OnlineConsultationTimings.objects.create(
                    doctor=doctor_profile,
                    day=day,
                    start_time="",
                    end_time=""
                )

print("Done")


