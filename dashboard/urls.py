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
                                   item_update_event, remove_item_from_event, edit_item,
                                   stock_full_edit, new_stock, parameters, add_stock_param)
from dashboard.views.categories import categories
from dashboard.views.locations import locations
from dashboard.views.events import (events, new_event, view_event_items,
                                    remove_event_item, event_detail, delete_event)
from dashboard.views.orders import orders, order_details, cancel_order

urlpatterns = [
    path('', dashboard_home, name="dashboard_home"),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('items/<int:item_id>/edit/add_stock_param/', add_stock_param, name="add_stock_param"),
    path('items/<int:item_id>/edit/', edit_item, name="edit_item"),
    path('items/<int:item_id>/new/', new_stock, name="new_stock"),
    path('items/<int:item_id>/<int:stock_id>/edit', stock_full_edit, name="stock_edit"),
    path('items/<int:item_id>/', item_detail, name="item_detail"),
    path('items/update-stock-quantity/<int:item_id>/', item_update_stock_quantity, name="item_update_stock_quantity"),
    path('items/update-event/<int:item_id>/', item_update_event, name="item_update_event"),
    path('items/remove-event/<int:item_id>/', remove_item_from_event, name="remove_item_from_event"),
    path('items/parameters/', parameters, name="parameters"),
    path('items/', item_list, name="items"),

    path('categories/', categories, name="categories"),
    path('locations/', locations, name="locations"),
    path('events/', events, name="events"),
    path('events/<int:event_id>/', event_detail, name="event_detail"),
    path('events/delete-event/<int:event_id>/', delete_event, name="delete_event"),
    path('events/view-items/<int:event_id>/', view_event_items, name="event_view_items"),
    path('events/remove-items/<int:event_id>/', remove_event_item, name="remove_event_item"),
    path('events/new/', new_event, name="new_event"),
    path('orders/<int:order_id>/cancel', cancel_order, name="cancel_order"),
    path('orders/<int:order_id>/', order_details, name="order_details"),
    path('orders/', orders, name="orders"),
]

app_name = 'dashboard'
