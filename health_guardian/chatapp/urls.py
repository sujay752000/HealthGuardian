
from django.urls import path
from . import views


urlpatterns = [
    path("chat/<str:room>", views.userOnlineChat, name="chat" )
]
