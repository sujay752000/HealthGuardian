from django import forms
from django.contrib.auth.models import User
from accounts.models import DoctorProfile

class AdminDoctorUserViewForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'date_joined']


class AdminDoctorProfileViewForm(forms.ModelForm):

    class Meta:
        model = DoctorProfile
        exclude = ['user', 'photo', 'admin_approved', 'resume', 'qualification_certificate']


