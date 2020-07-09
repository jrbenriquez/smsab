from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from inventory.models.events import Event

@login_required()
def events(request):
    events = Event.objects.all
    context = {"events": events}
    return render(request, 'dashboard/events.html', context=context)
