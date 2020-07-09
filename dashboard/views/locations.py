from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from inventory.models.locations import Location


@login_required
def locations(request):
    locations = Location.objects.all
    return render(request, 'dashboard/locations.html', context={"locations": locations})
