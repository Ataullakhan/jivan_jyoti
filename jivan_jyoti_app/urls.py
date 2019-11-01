from django.urls import path
from jivan_jyoti_app import views


urlpatterns = [
    path('registration_form/', views.registration_form, name='registration_form'),
]
