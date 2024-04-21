from django import forms
from django.contrib.auth.models import User
from .models import ClinicDetails, ClinicAppointmnetTimings, OnlineConsultationTimings, DoctorOffDays
from django.forms import BaseFormSet, ValidationError, BaseModelFormSet
from django.utils.translation import gettext as _
from accounts.models import DoctorProfile
from datetime import date


class DoctorUserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError("First name is required")
        if len(first_name) < 1:
            raise forms.ValidationError("Enter a valid name")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError("Last name is required")
        if len(last_name) < 1:
            raise forms.ValidationError("Enter a valid name")
        return last_name


class DoctorProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'experiance']

    def clean_experiance(self):
        experiance = self.cleaned_data.get('experiance')
        if not experiance or experiance >= 100:
            raise forms.ValidationError("Enter a valid no : of experiance")
        return experiance
    


class ClinicRegisterForm(forms.ModelForm):

    class Meta:
        model = ClinicDetails
        exclude = ["doctor"]


class ClinicAppointmentTimingsRegisterForm(forms.ModelForm):

    class Meta:
        model = ClinicAppointmnetTimings
        exclude = ["doctor", "day"]

class ClinicAppointmentTimingsUpdateForm(forms.ModelForm):

    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)

    class Meta:
        model = ClinicAppointmnetTimings
        exclude = ["doctor"]

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and not end_time:
            raise ValidationError("End time is required if start time is provided.")

        if end_time and not start_time:
            raise ValidationError("Start time is required if end time is provided.")

        if not start_time and not end_time:
            return cleaned_data 

        if start_time or end_time:
            if not start_time:
                raise ValidationError("Start time is required.")
            if not end_time:
                raise ValidationError("End time is required.")

        return cleaned_data


class OnlineAppointmentTimingsUpdateForm(forms.ModelForm):

    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)

    class Meta:
        model = OnlineConsultationTimings
        exclude = ["doctor"]

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and not end_time:
            raise ValidationError("End time is required if start time is provided.")

        if end_time and not start_time:
            raise ValidationError("Start time is required if end time is provided.")

        if not start_time and not end_time:
            return cleaned_data 

        if start_time or end_time:
            if not start_time:
                raise ValidationError("Start time is required.")
            if not end_time:
                raise ValidationError("End time is required.")

        return cleaned_data



class OnlineConsultationTimingsRegisterForm(forms.ModelForm):

    class Meta:
        model = OnlineConsultationTimings
        exclude = ["doctor", "day"]


def validate_date_not_in_past(value):
    if value < date.today():
        raise ValidationError('Date cannot be in the past.')

class DoctorOffDaysRegisterForm(forms.ModelForm):
    date = forms.DateField(
        label='Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Select date from today onwards',
        validators=[validate_date_not_in_past]
    )

    class Meta:
        model = DoctorOffDays
        exclude = ["doctor"]
        


class BaseAppointmentFormSet(BaseFormSet):
    def clean(self):
        super().clean()
        missing_time_errors = []
        any_form_filled = False
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for form in self.forms:
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            form_day_str = form.prefix[-1]
            form_day_int = int(form_day_str)
            day = days_of_week[form_day_int]

            if start_time and not end_time:
                missing_time_errors.append(
                    f"Please provide End Time for {day} ."
                )
                any_form_filled = True
            
            if end_time and not start_time:
                missing_time_errors.append(
                    f"Please provide Start Time for {day}."
                )
                any_form_filled = True

            if start_time and end_time:
                any_form_filled = True

        if missing_time_errors:
            raise ValidationError(missing_time_errors)
        
        if not any_form_filled:
            raise ValidationError(f"Please fill the time schedule")


class BaseAppointmentFormSetUpdate(BaseModelFormSet):
    def clean(self):
        super().clean()
        missing_time_errors = []
        any_form_filled = False
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for form in self.forms:
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            form_day_str = form.prefix[-1]
            form_day_int = int(form_day_str)
            day = days_of_week[form_day_int]

            if start_time and not end_time:
                missing_time_errors.append(
                    f"Please provide End Time for {day} ."
                )
                any_form_filled = True
            
            if end_time and not start_time:
                missing_time_errors.append(
                    f"Please provide Start Time for {day}."
                )
                any_form_filled = True

            if start_time and end_time:
                any_form_filled = True

        if missing_time_errors:
            raise ValidationError(missing_time_errors)
        
        if not any_form_filled:
            raise ValidationError(f"Please fill the time schedule")
        

