from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import login as app_login
from django.contrib.auth import logout as app_logout
from django.http import HttpResponse

from chatbot.models.users import MessengerProfile
User = get_user_model()


def login(request):

    if request.method == 'GET':
        next = request.GET.get('next', None)
        context = {}
        if next:
            context['next'] = next
        return render(request, 'dashboard/login.html', context=context)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        next = request.GET.get('next')
        errors = []
        if not email:
            errors.append('Please enter email')
        if not password:
            errors.append('Please enter password')

        user = User.objects.filter(email=email).first()
        if not user:
            errors.append('Invalid Credentials')
        if user:
            valid = user.check_password(password)
            if not valid and 'Invalid Credentials' not in errors:
                errors.append('Invalid Credentials')

        if errors:
            context = {"errors": errors}
            return render(request, 'dashboard/login.html', context=context)

        app_login(request, user)
        if next:
            return redirect(next)
        return redirect(settings.REDIRECT_URL)


def logout(request):
    if request.method == 'POST':
        app_logout(request)
        return HttpResponse('OK')


@login_required
def dashboard_home(request):
    profiles = MessengerProfile.objects.all().order_by('-joined')
    context = {'profiles': profiles}
    return render(request, 'dashboard/index.html', context=context)
