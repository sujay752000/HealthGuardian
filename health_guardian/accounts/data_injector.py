from django.contrib.auth.models import User, Group
from accounts.models import DoctorProfile, SPECIALIZATIONS
from faker import Faker
from random import sample

# Assuming SPECIALIZATIONS list is already defined

# Define the number of doctors to add for each specialization
num_doctors_per_specialization = 5

# Initialize Faker to generate random names
fake = Faker()

# Iterate over each specialization
for specialization_key, specialization_value in SPECIALIZATIONS:
    # Create User instances for the current specialization
    users_for_specialization = []
    for i in range(num_doctors_per_specialization):
        # Generate random first name and last name
        first_name = fake.first_name()
        last_name = fake.last_name()

        # Combine first name and a suffix to create the username
        username = f"{first_name.lower()}@doctor"  # Username format: first_name@doctor
        email = "sujayprasad010@gmail.com"
        password = "amma@123"
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        
        # Assign the user to the "doctor" group
        group = Group.objects.get_or_create(name='doctor')
        group[0].user_set.add(user)

        users_for_specialization.append(user)

    # Create DoctorProfile instances for each user
    for i, user in enumerate(users_for_specialization, start=1):
        # Set experience based on loop iteration
        experience = i * 2  # Example: Increase experience with each iteration

        doctor_profile = DoctorProfile.objects.create(
            user=user,
            specialization=specialization_value,
            experience=experience,
        )

        # You can also upload photo, qualification_certificate, resume, etc. here
