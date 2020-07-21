from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from inventory.models.orders import Order
from django.db.models import Q


@login_required
def orders(request):
    orders = Order.objects.all()
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    search_text = request.GET.get('search')
    status = int(request.GET.get('status', 1))
    order_by = request.GET.get('order_by')

    if status:
        orders = orders.filter(status=status)

    if order_by:
        orders = orders.order_by(order_by)

    search_fields = ['id', 'stocks__stock__item__name', 'buyer']
    search_dict = {}

    for field in search_fields:
        search_dict[field] = request.GET.get(field)

    if search_text:
        id_search_query = Q(id__icontains=search_text)
        stock_name_query = Q(stocks__stock__item__name__icontains=search_text)
        buyer_query = Q(buyer__provided_name__icontains=search_text)

        orders = orders.filter(id_search_query | stock_name_query | buyer_query)

    paginator = Paginator(orders, page_size)
    page_obj = paginator.get_page(page_number)

    order_class = Order
    context = {"orders": orders,
               "page_obj": page_obj,
               "order_class": order_class,
               "current_status_filter": status}
    return render(request, 'dashboard/orders.html', context=context)


@login_required
def order_details(request, order_id):
    order = Order.objects.get(id=order_id)
    order_class = Order
    context = {
        "order": order,
        "order_class": order_class,
    }
    return render(request, 'dashboard/orders/order_details.html', context=context)


@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.cancel(request.user)
    context = {"order": order}
    return redirect(reverse('dashboard:order_details', kwargs={'order_id': order.id}))


@login_required
def change_status(request, order_id):
    order = Order.objects.get(id=order_id)
    status = request.POST.get('new_status', None)
    if status:
        order.status = status
        order.save(update_fields=['status'])
    context = {"order": order}
    return redirect(reverse('dashboard:order_details', kwargs={'order_id': order.id}))

