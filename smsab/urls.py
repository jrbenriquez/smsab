"""smsab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import reverse, redirect
from authentication.views import set_cookie

from django.conf.urls.static import static
from django.conf import settings


def go_to_home(request):
    return redirect(reverse('dashboard:dashboard_home'))


urlpatterns = [
    path('', go_to_home, name='home'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls', namespace="dashboard")),
    path('api/v1/', include('api.urls')),
    path('auth/', include('authentication.urls')),
    path('authorize', set_cookie, name='set-cookie')
] + static(settings.MEDIAFILES_LOCATION, document_root=settings.MEDIA_ROOT)
