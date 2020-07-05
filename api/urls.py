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
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from .views import categories, locations, items


router = DefaultRouter()

router.register(r'category', categories.CategoryViewSet, 'categories')
router.register(r'location', locations.LocationViewSet, 'locations')
router.register(r'item', items.ItemViewSet, 'item')
urlpatterns = [
    url(r'^', include(router.urls)),
]

app_name = 'api'
