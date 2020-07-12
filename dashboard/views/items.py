from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from inventory.models.categories import Category
from inventory.models.locations import Location
from inventory.models.events import Event
from inventory.models.items import ParameterTemplate, Item, Parameter, ItemStock


@login_required
def item_list(request):
    items = Item.objects.all()
    page_number = request.GET.get('page')
    page_size = request.GET.get('page_size')
    category_filter = request.GET.get('category')
    search_text = request.GET.get('search')
    if not page_number:
        page_number = 1
    if not page_size:
        page_size = 5
    if category_filter:
        items = items.filter(category__id=category_filter)
    if search_text:
        items = items.filter(name__icontains=search_text)
    paginator = Paginator(items, page_size)
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    locations = Location.objects.all()
    ptemplates = ParameterTemplate.objects.all().order_by('name')
    context = {
        "items": items,
        "page_obj": page_obj,
        "categories": categories,
        "locations": locations,
        "ptemplates": ptemplates,
    }
    return render(request, 'dashboard/items.html', context=context)


@login_required
def item_update_stock_quantity(request, item_id):
    if request.method == 'POST':
        data = request.POST.copy()
        for d in data:
            if 'stock' in d:
                stock_id = d.split('-')[-1]
                item = Item.objects.get(id=item_id)
                stock = item.stocks.get(id=stock_id)
                stock.quantity = data[d]
                stock.save(update_fields=['quantity'])

        return redirect(reverse('dashboard:item_detail', kwargs={'item_id': item_id}))
    return redirect(reverse('dashboard:items'))


@login_required
def item_update_event(request, item_id):
    if request.method == 'POST':
        data = request.POST.copy()
        for d in data:
            if 'event' in d:
                item = Item.objects.get(id=item_id)
                event = Event.objects.get(id=data[d])
                event.add_item(item)

        return redirect(reverse('dashboard:item_detail', kwargs={'item_id': item_id}))
    return redirect(reverse('dashboard:items'))


@login_required
def remove_item_from_event(request, item_id):
    if request.method == 'POST':
        data = request.POST.copy()
        for d in data:
            if 'event' in d:
                item = Item.objects.get(id=item_id)
                event = Event.objects.get(id=data[d])
                event.remove_item(item)
        return redirect(reverse('dashboard:item_detail', kwargs={'item_id': item_id}))
    return redirect(reverse('dashboard:items'))


@login_required
def item_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    categories = Category.objects.all()
    locations = Location.objects.all()
    events = Event.objects.exclude(items_featured__item=item)
    update_event_url = reverse('dashboard:item_update_event', kwargs={"item_id": item_id})
    remove_event_url = reverse('dashboard:remove_item_from_event', kwargs={"item_id": item_id})
    context = {
        "item": item,
        "categories": categories,
        "locations": locations,
        "events": events,
        "update_event_url": update_event_url,
        "remove_event_url": remove_event_url
    }
    return render(request, 'dashboard/items/item_detail.html', context=context)

