"""jivan_jyoti URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls.conf import path
from jivan_jyoti_app import views
from jivan_jyoti import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration_form/', views.registration_form, name='registration_form'),
    path('admin_registration/', views.admin_registration, name='admin_registration'),
    path('volunteer_registration/', views.volunteer_registration, name='volunteer_registration'),
    path('fatch_ragistration_data/', views.fatch_ragistration_data),
    path('fatch_volunteer_data/', views.fatch_volunteer_data),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
