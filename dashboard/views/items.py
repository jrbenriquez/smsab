from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from api.serializers.items import ItemSerializer, ItemPhotoSerializer, ItemStockSerializer, ParameterTemplateSerializer
from inventory.models.categories import Category
from inventory.models.locations import Location
from inventory.models.events import Event
from inventory.models.items import ParameterTemplate, Item, Parameter, ItemStock, ParameterItemRelation


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
    items = items.order_by('-created_at')
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


@login_required
def stock_full_edit(request, item_id, stock_id):
    item = Item.objects.get(id=item_id)
    stock = ItemStock.objects.get(id=stock_id)
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
        "remove_event_url": remove_event_url,
        "stock": stock
    }

    if request.method == 'GET':
        return render(request, 'dashboard/items/stock_detail.html', context=context)
    elif request.method == 'POST':
        def perform_update(serializer, data={}, files={}):

            model_obj = serializer.save()

            if item.get_variation_count == 1:
                item.price = model_obj.price
                item.save(update_fields=['price'])
            created_params = {}

            for d in data:
                if 'param' in d:
                    param_name = d.split('-')[-1]
                    param_value = data[d]
                    try:
                        created_params[param_name] = param_value
                        stocks = model_obj.item.stocks.all().exclude(id=model_obj.id)

                        for stock in stocks:
                            current_params = {}
                            relations = stock.parameters.all()

                            for r in relations:
                                current_params[r.parameter.name] = r.parameter.value

                            if current_params == created_params:
                                raise IntegrityError('Existing Params for Items')
                    except IntegrityError as e:
                        errors = ['Parameters entered already exists for current item']
                        context['errors'] = errors
                        return render(request, 'dashboard/items/stock_detail.html', context=context)

            for d in data:
                if 'param' in d:
                    param_name = d.split('-')[-1]
                    param_value = data[d]
                    try:
                        created_params[param_name] = param_value
                        model_obj.update_param(param_name, param_value, created_params)
                    except IntegrityError as e:
                        errors = ['Parameters entered already exists for current item']
                        context['errors'] = errors
                        return render(request, 'dashboard/items/stock_detail.html', context=context)


            photo = files.get('photo')
            if photo or photo == 'undefined':

                photo_serializer = ItemPhotoSerializer(data={
                    "item": model_obj.id,
                    "photo": photo
                })
                valid = photo_serializer.is_valid(raise_exception=False)
                if valid:
                    photo_serializer.save()
            return redirect(reverse('dashboard:item_detail', kwargs={"item_id": item.id}))



        serializer = ItemStockSerializer(stock, data=request.POST, partial=True)
        serializer.is_valid(raise_exception=True)
        return perform_update(serializer, data=request.POST, files=request.FILES)



@login_required
def new_stock(request, item_id):
    item = Item.objects.get(id=item_id)
    categories = Category.objects.all()
    locations = Location.objects.all()
    events = Event.objects.exclude(items_featured__item=item)
    update_event_url = reverse('dashboard:item_update_event', kwargs={"item_id": item_id})
    remove_event_url = reverse('dashboard:remove_item_from_event', kwargs={"item_id": item_id})
    ptemplates = ParameterTemplate.objects.all().order_by('name').filter(name__in=item.get_params)
    context = {
        "item": item,
        "categories": categories,
        "locations": locations,
        "events": events,
        "update_event_url": update_event_url,
        "remove_event_url": remove_event_url,
        "ptemplates": ptemplates
    }

    if request.method == 'GET':
        return render(request, 'dashboard/items/new_stock.html', context=context)
    elif request.method == 'POST':
        def perform_create(serializer, data={}, files={}):

            model_obj = serializer.save()

            if item.get_variation_count == 1:
                item.price = model_obj.price
                item.save(update_fields=['price'])
            hits = []
            errors = []
            created_params = {}
            for d in data:
                if 'param' in d:
                    param_name = d.split('-')[-1]
                    param_value = data[d]

                    parameter, created = Parameter.objects.get_or_create(name=param_name,
                                                                         value=param_value)

                    param_relation = ParameterItemRelation.objects.create(
                        item=model_obj.item, stock=model_obj, parameter=parameter)
                    created_params[param_name] = param_value

            stocks = item.stocks.all().exclude(id=model_obj.id)

            for stock in stocks:
                current_params = {}
                relations = stock.parameters.all()

                for r in relations:
                    current_params[r.parameter.name] = r.parameter.value
                print(f"{current_params} - {created_params}")
                if current_params == created_params:
                    model_obj.delete()
                    errors = ['Parameters entered already exists for current item or maybe you forgot to type parameter value']
                    context['errors'] = errors
                    return render(request, 'dashboard/items/new_stock.html', context=context)

            photo = files.get('photo')
            if photo or photo == 'undefined':

                photo_serializer = ItemPhotoSerializer(data={
                    "item": model_obj.id,
                    "photo": photo
                })
                valid = photo_serializer.is_valid(raise_exception=False)
                if valid:
                    photo_serializer.save()
            return redirect(reverse('dashboard:item_detail', kwargs={"item_id": item.id}))

        data = request.POST.copy()
        data['item'] = item.id
        errors = []
        price = data.get('price')
        quantity = data.get('quantity')

        if not price:
            errors.append('Price required for new stock')

        if not quantity:
            errors.append('Quantity required for new stock')

        serializer = ItemStockSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            errors.append(e)
        if errors:
            context['errors'] = errors
            return render(request, 'dashboard/items/new_stock.html', context=context)
        return perform_create(serializer, data=request.POST, files=request.FILES)




@login_required
def edit_item(request, item_id):
    item = Item.objects.get(id=item_id)
    categories = Category.objects.all()
    locations = Location.objects.all()
    events = Event.objects.exclude(items_featured__item=item)
    update_event_url = reverse('dashboard:item_update_event', kwargs={"item_id": item_id})
    remove_event_url = reverse('dashboard:remove_item_from_event', kwargs={"item_id": item_id})
    ptemplates = ParameterTemplate.objects.all().order_by('name').exclude(name__in=item.get_params)
    context = {
        "item": item,
        "categories": categories,
        "locations": locations,
        "events": events,
        "update_event_url": update_event_url,
        "remove_event_url": remove_event_url,
        "ptemplates": ptemplates
    }
    if request.method == 'GET':

        return render(request, 'dashboard/items/edit_item.html', context=context)

    elif request.method == 'POST':
        def perform_update(serializer, data={}, files={}):

            model_obj = serializer.save()

            photo = files.get('photo')
            if photo or photo == 'undefined':

                photo_serializer = ItemPhotoSerializer(data={
                    "item": model_obj.id,
                    "photo": photo
                })
                valid = photo_serializer.is_valid(raise_exception=False)
                if valid:
                    photo_serializer.save()

        serializer = ItemSerializer(item, data=request.POST, partial=True)
        serializer.is_valid(raise_exception=True)
        perform_update(serializer, data=request.POST, files=request.FILES)
        return redirect(reverse('dashboard:item_detail', kwargs={"item_id": item.id}))


@login_required
def parameters(request):
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
    items = items.order_by('-created_at')
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

    if request.method == 'GET':
        return render(request, 'dashboard/items.html', context=context)
    elif request.method == 'POST':
        serializer = ParameterTemplateSerializer(data=request.POST)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            context['param_errors'] = [e,]
        return render(request, 'dashboard/items.html', context=context)


@login_required
def add_stock_param(request, item_id):
    item = Item.objects.get(id=item_id)
    categories = Category.objects.all()
    locations = Location.objects.all()
    events = Event.objects.exclude(items_featured__item=item)
    update_event_url = reverse('dashboard:item_update_event', kwargs={"item_id": item_id})
    remove_event_url = reverse('dashboard:remove_item_from_event', kwargs={"item_id": item_id})
    ptemplates = ParameterTemplate.objects.all().order_by('name').exclude(name__in=item.get_params)
    context = {
        "item": item,
        "categories": categories,
        "locations": locations,
        "events": events,
        "update_event_url": update_event_url,
        "remove_event_url": remove_event_url,
        "ptemplates": ptemplates
    }
    if request.method == 'GET':

        return render(request, 'dashboard/items/edit_item.html', context=context)

    elif request.method == 'POST':
        template_id = request.POST.get('add-param')
        if not template_id:
            context["errors"] = ["Missing Template ID"]

        item.create_stock_param(template_id)
        ptemplates = ParameterTemplate.objects.all().order_by('name').exclude(name__in=item.get_params)
        context['ptemplates'] = ptemplates
        return render(request, 'dashboard/items/edit_item.html', context=context)




