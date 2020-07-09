from django.shortcuts import render, redirect
from inventory.models.events import Event


def events(request):
    events = Event.objects.all
    context = {"events": events}
    return render(request, 'dashboard/events.html', context=context)
