from django.urls import path
from . import views

urlpatterns = [
    path('', views.newsFeeds, name="news_feed" )
]