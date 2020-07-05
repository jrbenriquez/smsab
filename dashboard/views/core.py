from django.shortcuts import render, redirect


def dashboard_home(request):
    return render(request, 'dashboard/index.html', context={})
