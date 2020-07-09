from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from inventory.models.categories import Category
from inventory.models.locations import Location
from inventory.models.items import ParameterTemplate, Item

@login_required()
def item_list(request):
    items = Item.objects.all()
    categories = Category.objects.all()
    locations = Location.objects.all()
    ptemplates = ParameterTemplate.objects.all().order_by('name')
    context = {
        "items": items,
        "categories": categories,
        "locations": locations,
        "ptemplates": ptemplates,
    }
    return render(request, 'dashboard/items.html', context=context)
