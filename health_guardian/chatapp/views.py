from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from patient.models import OnlineConsultationPassKeys
from accounts.views import is_patient, is_doctor, is_admin, dashboardRedirector
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from patient.models import PatientProfile
from accounts.models import DoctorProfile
from .models import Message

# Create your views here.



# @login_required(login_url='app_home')
# def userOnlineChat(request):
#     booking_id = request.GET.get('booking_id')
#     doctor_id = request.GET.get('doctor_id')
#     patient_id = request.GET.get('patient_id')
#     pass_key_obj = get_object_or_404(OnlineConsultationPassKeys, booking_instance=booking_id, doctor=doctor_id, patient=patient_id )
#     pass_key = pass_key_obj.pass_key
#     if pass_key_obj:
#         room = pass_key
#         messages = Message.objects.filter(room=pass_key_obj)


#         sender_photos = []
#         for message in messages:
#             sender_photos.append(message.sender_photo())

#         messages_with_photos = zip(messages, sender_photos)

#         print(messages)

#         extended_template = None
#         if is_admin(request.user):
#             extended_template = "admin-app/admin_dashboard.html"
#         elif is_patient(request.user):
#             extended_template = "patient-app/patient_dashboard.html"
#         elif is_doctor(request.user):
#             extended_template = "doctor-app/doctor_dashboard.html"
        
#         name = request.user.get_full_name()
#         username = request.user.username

#         if request.is_secure():
#             protocol = 'https'
#         else:
#             protocol = 'http'

#         url_join = protocol + "://" + str(get_current_site(request)) + f"/onlinechat/chat?roomID={pass_key}&booking_id={booking_id}&doctor_id={doctor_id}&patient_id={patient_id}"

#         details = {
#             'name': name,
#             'room': room,
#             'current_username': username,
#             'extended_template': extended_template,
#             'url_join': url_join,
#             'grp_messages': messages_with_photos,
#             'sender_photos': sender_photos,
#             'booking_id': booking_id,
#             'doctor_id': doctor_id,
#             'patient_id': patient_id
#         }

#         return render(request, 'chatroom.html', context=details)
#     else:
#         messages.error(request, "Invalid Meeting")
#         return dashboardRedirector(request.user)


@login_required(login_url='app_home')
def userOnlineChat(request, room):
    room_obj = get_object_or_404(OnlineConsultationPassKeys, pass_key=room)
    # room_obj = OnlineConsultationPassKeys.objects.get(pass_key=room)
    messages = Message.objects.filter(room=room_obj)
    sender_photos = []
    for message in messages:
        sender_photos.append(message.sender_photo())

    messages_with_photos = zip(messages, sender_photos)

    extended_template = None
    if is_admin(request.user):
        extended_template = "admin-app/admin_base.html"
    elif is_patient(request.user):
        extended_template = "patient-app/patient_base.html"
    elif is_doctor(request.user):
        extended_template = "doctor-app/doctor_base.html"
    
    name = request.user.get_full_name()
    username = request.user.username

    details = {
        'name': name,
        'room': room,
        'current_username': username,
        'extended_template': extended_template,
        # 'url_join': url_join,
        'grp_messages': messages,
        'sender_photos': sender_photos,
    }

    return render(request, 'room.html', context=details)


