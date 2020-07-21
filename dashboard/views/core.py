from django.conf import settings
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import login as app_login
from django.contrib.auth import logout as app_logout
from django.http import HttpResponse

from chatbot.models.users import MessengerProfile
from inventory.models import Item, Order, MarketingProfile, OperationsProfile
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


def activate_marketing(request):

    context = {}
    if request.method == 'GET':
        return render(request, 'dashboard/users/marketing_profile.html', context=context)

    elif request.method == 'POST':
        email = request.POST.get('email')
        user = MarketingProfile.objects.filter(user__email=email, user__password='')
        if not user:
            context['errors'] = ['Email not found on team']
            return render(request, 'dashboard/users/marketing_profile.html', context=context)
        else:
            user = user.get().user
            app_login(request, user)
            return redirect(reverse('dashboard:setup_password'))


def activate_operations(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'dashboard/users/operations_profile.html', context=context)

    elif request.method == 'POST':
        email = request.POST.get('email')
        user = OperationsProfile.objects.filter(user__email=email, user__password='')
        if not user:
            context['errors'] = ['Email not found on team']
            return render(request, 'dashboard/users/operations_profile.html', context=context)
        else:
            user = user.get().user
            app_login(request, user)
            return redirect(reverse('dashboard:setup_password'))


@login_required
def setup_password(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'dashboard/users/setup_password.html', context=context)
    elif request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        user = request.user
        print(user.first_name)
        if password != confirm_password:
            context['errors'] = ['Passwords do not match']
            return render(request, 'dashboard/users/setup_password.html', context=context)

        user.set_password(password)
        user.save(update_fields=['password'])
        app_login(request, user)
        return redirect(reverse('dashboard:dashboard_home'))




@login_required
def dashboard_home(request):
    profiles = MessengerProfile.objects.all().order_by('-joined')
    orders = Order.objects.all()
    items = Item.objects.all()
    new_subscribers = profiles[:10]
    context = {
        'profiles': profiles,
        'orders': orders,
        'items': items,
        'new_subscribers': new_subscribers
    }
    return render(request, 'dashboard/index.html', context=context)
