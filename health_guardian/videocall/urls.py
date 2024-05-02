
from django.urls import path, include
from . import views


urlpatterns = [
    path("videocall", views.userVideoCall, name="videocall" )
]
