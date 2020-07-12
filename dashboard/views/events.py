import pytz

from dateutil.parser import parse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from api.serializers.events import EventSerializer, EventPhotoSerializer

from inventory.models.events import Event
from inventory.models.items import Item


@login_required
def events(request):
    events = Event.objects.all
    context = {"events": events}
    return render(request, 'dashboard/events.html', context=context)


@login_required
def new_event(request):

    if request.method == 'GET':
        context = {}
        return render(request, 'dashboard/events/new_event.html', context=context)

    elif request.method == 'POST':
        try:
            data = request.POST.copy()
            data['start'] = parse(data['start']).replace(tzinfo=pytz.timezone('Asia/Manila'))
            data['end'] = parse(data['end']).replace(tzinfo=pytz.timezone('Asia/Manila'))
            serializer = EventSerializer(data=data)

            serializer.is_valid(raise_exception=True)

            model_obj = serializer.save()

            photo = request.FILES.get('photo')
            if photo:
                photo_serializer = EventPhotoSerializer(data={
                    "event": model_obj.id,
                    "photo": photo
                })
                photo_serializer.is_valid()
                photo_serializer.save()

            return redirect(reverse('dashboard:event_view_items', kwargs={'event_id': model_obj.id}))
        except Exception as e:
            errors = [e,]
            context = {"errors": errors,
                       "previous_request": request
                       }
            return render(request, 'dashboard/events/new_event.html', context=context)


@login_required
def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    context = {"event": event}

    if request.method == 'GET':
        context['delete_event_url'] = reverse('dashboard:delete_event', kwargs={'event_id': event_id})

    elif request.method == 'POST':
        data = request.POST.copy()
        data['start'] = parse(data['start'])
        data['end'] = parse(data['end'])
        serializer = EventSerializer(event, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        photo = request.FILES.get('photo')
        if photo:
            photo_serializer = EventPhotoSerializer(data={
                "event": event.id,
                "photo": photo
            })
            photo_serializer.is_valid()
            photo_serializer.save()
        return redirect(reverse('dashboard:events'))

    return render(request, 'dashboard/events/event_detail.html', context=context)


@login_required
def delete_event(request, event_id):

    if request.method == 'POST':
        event = Event.objects.get(id=event_id)
        event.delete()
        return redirect(reverse('dashboard:events'))


@login_required
def view_event_items(request, event_id):
    event = Event.objects.get(id=event_id)
    item_relations = event.items_featured.all()
    add_item_search_text = request.GET.get('add_item_search_text')
    items = None
    if add_item_search_text:
        items = Item.objects.filter(name__icontains=add_item_search_text)

    if request.method == 'GET':
        remove_item_url = reverse('dashboard:remove_event_item', kwargs={"event_id": event_id})
        context = {
            'event': event,
            "item_relations": item_relations,
            "items": items,
            "remove_item_url": remove_item_url
        }
        return render(request, 'dashboard/events/view_items.html', context=context)

    elif request.method == 'POST':
        try:
            data = request.POST.copy()
            for d in data:
                if 'add' in d:
                    item = Item.objects.get(id=data[d])
                    event.add_item(item)
            return redirect(reverse('dashboard:event_view_items', kwargs={"event_id":event_id}))
        except Exception as e:
            context = {
                'event': event,
                "item_relations": item_relations,
                "items": items
            }
            errors = [e,]
            context["errors"] = errors
            return render(request, 'dashboard/events/view_items.html', context=context)


@login_required
def remove_event_item(request, event_id):
    if request.method == 'POST':
        data = request.POST.copy()
        for d in data:
            if 'item' in d:
                item = Item.objects.get(id=data[d])
                event = Event.objects.get(id=event_id)
                event.remove_item(item)
        return redirect(reverse('dashboard:event_view_items', kwargs={'event_id': event_id}))
    return redirect(reverse('dashboard:events'))



