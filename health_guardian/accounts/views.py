from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegisterationForm, UserChangePasswordForm, UserPasswordReset, DoctorSignupForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.core.mail import EmailMessage
from health_guardian.settings import EMAIL_HOST_USER
from .tokens import account_activation_token
from django.contrib.auth.models import User, Group
from django.db.models.query_utils import Q
from health_guardian.settings import ADMIN_KEY
from django.template.loader import render_to_string
from .models import DoctorProfile

# Create your views here.

def is_admin(user):
    return user.groups.filter(name='admin').exists()
def is_patient(user):
    return user.groups.filter(name='patient').exists()
def is_doctor(user):
    return user.groups.filter(name='doctor').exists()

def dashboardRedirector(user):
    if is_admin(user):
        return redirect('admin_dashboard')
    elif is_patient(user):
        return redirect('patient_dashboard')
    elif is_doctor(user):
        doctor = DoctorProfile.objects.get(user=user.id)
        if doctor.admin_approved == True:
            return redirect('doctor_dashboard')
        else:
            return  redirect('doctor_notapproved')
    else:
        return redirect('app_home')


def sendAccountActivationEmail(request, user):
    to_user = user.email
    subject = "Please click the following link to activate your account"
    message = render_to_string('user/email_activation.html', {
        'name': user.get_full_name,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'domain' : get_current_site(request).domain,
        'token' : account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(subject=subject, body=message, from_email=EMAIL_HOST_USER, to=[to_user])
    email.content_subtype = 'html'
    email.send(fail_silently=True)


def activateEmail(request, uidb64, token):
    if request.user.is_authenticated:
        return dashboardRedirector(request.user)
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account verification successfull you can now login')
        return dashboardRedirector(user)
    else:
        messages.error(request, 'Account activation failed')
        return dashboardRedirector(user)


def sendAccountPasswordResetEmail(request, user):
    to_user = user.email
    subject = "Please click the following link to Reset your account"
    message = render_to_string('user/reset_password_email.html', {
        'name': user.get_full_name,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'domain' : get_current_site(request).domain,
        'token' : account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(subject=subject, body=message, from_email=EMAIL_HOST_USER, to=[to_user])
    email.content_subtype = 'html'
    email.send(fail_silently=True)



@login_required(login_url='app_home')
def userPasswordChange(request):
    extended_template = None
    if is_admin(request.user):
        extended_template = "admin-app/admin_dashboard.html"
    elif is_patient(request.user):
        extended_template = "patient-app/patient_dashboard.html"
    elif is_doctor(request.user):
        extended_template = "doctor-app/doctor_dashboard.html"
        
    form = UserChangePasswordForm(request.user)
    if request.method == 'POST':
        form = UserChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully changed password')
            return dashboardRedirector(request.user)
        else:
            for error in list(form.errors.values()):
                messages.error(request, f'{error}')

        return render(request, 'user/password_change.html', {'form': form, 'extended_template': extended_template})
    
    return render(request, 'user/password_change.html', {'form': form, 'extended_template': extended_template})



def userPasswordReset(request):
    if request.user.is_authenticated:
        return dashboardRedirector(request.user)
    
    form = UserPasswordReset()
    if request.method == 'POST':
        form = UserPasswordReset(request.POST)
        if form.is_valid():
            user_username = form.cleaned_data['username']
            user_email = form.cleaned_data['email']
            associated_user = User.objects.filter(Q(email=user_email) & Q(username=user_username)).first()
            if associated_user :
                sendAccountPasswordResetEmail(request, associated_user)
                messages.success(request, "Please check your mail box to reset your account")
                return dashboardRedirector(associated_user)
            else:
                return redirect("app_home")
        else:
            for error in list(form.errors.values()):
                messages.error(request, f'{error}')

    return render(request, 'user/user_password_reset.html', {'form': form})



def userPasswordResetActivation(request, uidb64, token):
    if request.user.is_authenticated:
        return dashboardRedirector(request.user)
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        form = UserChangePasswordForm(user)
        if request.method == 'POST':
            form = UserChangePasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Successfully changed password')
                return dashboardRedirector(user)
            else:
                for error in list(form.errors.values()):
                    messages.error(request, f'{error}')
        return render(request, 'user/user_password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'Activation Link expired')
        return redirect('app_home')



def userLogout(request):
    if request.user.is_authenticated:
        logout(request)

    return dashboardRedirector(request.user)


#########################################################################################################
############################################""" Patient """##############################################
#########################################################################################################

def patientSignup(request):
    if request.user.is_authenticated:
        return dashboardRedirector(request.user)

    user_form = UserRegisterationForm()
    if request.method == 'POST':
        user_form = UserRegisterationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False
            user.save()

            group = Group.objects.get_or_create(name='patient')
            group[0].user_set.add(user)
            
            sendAccountActivationEmail(request, user)
            messages.success(request, "Pease check your mail box to verify your account")
            return redirect('patient_login')
        else:
            messages.error(request, "Please enter your details correctly")
            return render(request, 'patient/patient_signup.html', {'form': user_form})

    return render(request, 'patient/patient_signup.html', {'form': user_form})




def patientLogin(request):
    if request.user.is_authenticated:
        return dashboardRedirector(request.user)
    
    if request.method == 'POST':
        user_username = request.POST.get('username')
        user_password = request.POST.get('password')

        user = authenticate(request, username=user_username, password=user_password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {user_username}')
            return dashboardRedirector(user)
        else:
            messages.error(request, 'Invalid Credentials')

    return render(request, 'patient/patient_login.html')


#########################################################################################################
############################################""" Doctor """###############################################
#########################################################################################################

def doctorSignup(request):
    if request.user.is_authenticated:
        return redirect('app_home')
    
    user_form = UserRegisterationForm()
    doctor_form = DoctorSignupForm()
    if request.method == "POST":
        user_form = UserRegisterationForm(request.POST)
        doctor_form = DoctorSignupForm(request.POST, request.FILES)
        if user_form.is_valid() and doctor_form.is_valid():
            myuser = user_form.save(commit=False)
            myuser.is_active = False
            myuser.save()

            group = Group.objects.get_or_create(name='doctor')
            group[0].user_set.add(myuser)

            doctor = doctor_form.save(commit=False)
            doctor.user = myuser
            doctor.save()
            
            sendAccountActivationEmail(request, myuser)
            messages.success(request, "Please check your mail box to verify your account")
            return dashboardRedirector(myuser)
        else:
            messages.error(request, "Please enter your details correctly")
            return render(request, 'doctor/doctor_signup.html', {'form': user_form})
        
    return render(request, 'doctor/doctor_signup.html', {'form': user_form, 'doctor_form': doctor_form})



def doctorLogin(request):
    if request.user.is_authenticated:
        return dashboardRedirector(request.user)
    
    if request.method == "POST":
        user_username = request.POST.get("username")
        user_password = request.POST.get("password")

        user = authenticate(request, username=user_username, password=user_password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user_username}")
            return dashboardRedirector(user)
        else:
            messages.error(request, "Invalid Credentials")

    return render(request, "doctor/doctor_login.html")


@login_required(login_url='doctor_login')
@user_passes_test(is_doctor)
def doctorBeforeApproval(request):
    name = request.user.get_full_name
    messages.success(request, "Your account is under Processing")
    logout(request)
    return render(request, "doctor/doctor_before_approval.html", {'name': name})




#########################################################################################################
############################################""" Admin """################################################
#########################################################################################################


def adminSignup(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    user_form = UserRegisterationForm()
    if request.method == 'POST':
        admin_key = request.POST.get("admin_key")
        user_form = UserRegisterationForm(request.POST)
        if user_form.is_valid() and admin_key == ADMIN_KEY:
            user = user_form.save()

            group = Group.objects.get_or_create(name='admin')
            group[0].user_set.add(user)
            
            messages.success(request, "Account Created")
            return redirect('admin_login')
        else:
            messages.error(request, "Please enter your details correctly")
            return render(request, 'admin/admin_signup.html', {'form': user_form})

    return render(request, 'admin/admin_signup.html', {'form': user_form})



def adminLogin(request):
    if request.user.is_authenticated:
        return dashboardRedirector(request.user)
    
    if request.method == "POST":
        user_username = request.POST.get("username")
        user_password = request.POST.get("password")

        user = authenticate(request, username=user_username, password=user_password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user_username}")
            return dashboardRedirector(user)
        else:
            messages.error(request, "Invalid Credentials")

    return render(request, "admin/admin_login.html")
