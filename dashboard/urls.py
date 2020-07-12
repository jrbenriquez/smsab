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
from dashboard.views.items import (item_list, item_detail, item_update_stock_quantity,
                                   item_update_event, remove_item_from_event)
from dashboard.views.categories import categories
from dashboard.views.locations import locations
from dashboard.views.events import (events, new_event, view_event_items,
                                    remove_event_item, event_detail, delete_event)
from dashboard.views.orders import orders

urlpatterns = [
    path('', dashboard_home, name="dashboard_home"),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('items/', item_list, name="items"),
    path('items/<int:item_id>/', item_detail, name="item_detail"),
    path('items/update-stock-quantity/<int:item_id>/', item_update_stock_quantity, name="item_update_stock_quantity"),
    path('items/update-event/<int:item_id>/', item_update_event, name="item_update_event"),
    path('items/remove-event/<int:item_id>/', remove_item_from_event, name="remove_item_from_event"),
    path('categories/', categories, name="categories"),
    path('locations/', locations, name="locations"),
    path('events/', events, name="events"),
    path('events/<int:event_id>/', event_detail, name="event_detail"),
    path('events/delete-event/<int:event_id>/', delete_event, name="delete_event"),
    path('events/view-items/<int:event_id>/', view_event_items, name="event_view_items"),
    path('events/remove-items/<int:event_id>/', remove_event_item, name="remove_event_item"),
    path('events/new/', new_event, name="new_event"),
    path('orders/', orders, name="orders"),
]

app_name = 'dashboard'
