from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from .models import DoctorProfile

class UserRegisterationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required")
        email = email.lower()
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError("First name is required")
        if len(first_name) < 2:
            raise forms.ValidationError("Enter a valid name")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError("Last name is required")
        if len(last_name) < 2:
            raise forms.ValidationError("Enter a valid name")
        return last_name
    

class UserChangePasswordForm(SetPasswordForm):

    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']



class UserPasswordReset(PasswordResetForm):

    username = forms.CharField(max_length=120, min_length=2)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Username is required')
        return username


class DoctorSignupForm(forms.ModelForm):

    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'qualification_certificate', 'experiance', 'resume']

    def clean_experiance(self):
        experiance = self.cleaned_data.get('experiance')
        if not experiance or experiance >= 100:
            raise forms.ValidationError("Enter a valid no : of experiance")
        return experiance
    
