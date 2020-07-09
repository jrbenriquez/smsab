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
from authentication.views import set_cookie
from dashboard.views.core import dashboard_home, login, logout
from dashboard.views.items import item_list
from dashboard.views.categories import categories
from dashboard.views.locations import locations
from dashboard.views.events import events
from dashboard.views.orders import orders

urlpatterns = [
    path('', dashboard_home, name="dashboard_home"),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('items/', item_list, name="items"),
    path('categories/', categories, name="categories"),
    path('locations/', locations, name="locations"),
    path('events/', events, name="events"),
    path('orders/', orders, name="orders"),
]

app_name = 'dashboard'
