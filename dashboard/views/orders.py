from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse

from inventory.models.orders import Order


@login_required
def orders(request):
    orders = Order.objects.all
    context = {"orders": orders}
    return render(request, 'dashboard/orders.html', context=context)


@login_required
def order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {"order": order}
    return render(request, 'dashboard/orders/order_details.html', context=context)


@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.cancel(request.user)
    context = {"order": order}
    return redirect(reverse('dashboard:order_details', kwargs={'order_id': order.id}))
