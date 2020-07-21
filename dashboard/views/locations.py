from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from authentication.utils.permissions import permission_required
from inventory.models.locations import Location


@login_required
@permission_required('is_marketing')
def locations(request):
    locations = Location.objects.all
    return render(request, 'dashboard/locations.html', context={"locations": locations})
