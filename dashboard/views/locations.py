from django.shortcuts import render, redirect
from inventory.models.locations import Location


def locations(request):
    locations = Location.objects.all
    return render(request, 'dashboard/locations.html', context={"locations": locations})
