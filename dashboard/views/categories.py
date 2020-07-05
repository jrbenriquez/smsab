from django.shortcuts import render, redirect
from inventory.models.categories import Category


def categories(request):
    categories = Category.objects.all
    return render(request, 'dashboard/categories.html', context={"categories": categories})
