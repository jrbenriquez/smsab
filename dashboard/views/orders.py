from django.shortcuts import render, redirect
from inventory.models.orders import Order


def orders(request):
    orders = Order.objects.all
    context = {"orders": orders}
    return render(request, 'dashboard/orders.html', context=context)
