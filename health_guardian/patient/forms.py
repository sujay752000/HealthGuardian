from django import forms
from .models import PatientProfile
from django.contrib.auth.models import User

class PatientProfileForm(forms.ModelForm):

    class Meta:
        model = PatientProfile
        exclude = ["patient"]

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height > 500:
            raise forms.ValidationError("Enter a valid height in cm")
        return height
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age > 200:
            raise forms.ValidationError("Enter a valid age in yrs")
        return age
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight > 700:
            raise forms.ValidationError("Enter a valid weight in kgs")
        return weight
    

class PatientUserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

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
    
class PatientUpdateProfileForm(forms.ModelForm):
        
    class Meta:
        model = PatientProfile
        exclude = ["patient"]

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height > 500:
            raise forms.ValidationError("Enter a valid height in cm")
        return height
    
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age > 200:
            raise forms.ValidationError("Enter a valid age in yrs")
        return age
    
    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight > 700:
            raise forms.ValidationError("Enter a valid weight in kgs")
        return weight
