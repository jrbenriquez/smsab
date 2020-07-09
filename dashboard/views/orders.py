from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from inventory.models.orders import Order


@login_required
def orders(request):
    orders = Order.objects.all
    context = {"orders": orders}
    return render(request, 'dashboard/orders.html', context=context)
