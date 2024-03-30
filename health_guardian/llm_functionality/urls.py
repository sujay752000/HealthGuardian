
from django.urls import path, include
from . import views


urlpatterns = [
    path('diet/<str:disease>', views.generate_diet, name='diet'),
    path('precaution/<str:disease>', views.generate_precaution, name='precaution')
]