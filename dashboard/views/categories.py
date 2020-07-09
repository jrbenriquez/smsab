from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from inventory.models.categories import Category

@login_required
def categories(request):
    categories = Category.objects.all
    return render(request, 'dashboard/categories.html', context={"categories": categories})
