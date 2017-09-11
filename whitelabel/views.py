from functools import lru_cache

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.http import HttpResponseNotAllowed

from whitelabel.models import Profile


def index(request):
    return render(
        request,
        'whitelabel/index.html',
        {
            "background_color": '#000000'
        }
    )


def signup(request, company_id):
    # https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
    company = Group.objects.get(id=company_id)
    company_name = company.name
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.company = company
            user.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            # login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form, 'company_name': company_name})


def confirm_new_account(request, user_uuid):
    if not request.user.is_authenticated:
        redirect('login')
    new_user_profile = Profile.objects.get(uuid=user_uuid)
    if request.user.profile.company_id != new_user_profile.company_id:
        raise HttpResponseNotAllowed
    new_user_profile.is_verified = True
    new_user_profile.save()
    return render(request, 'success.html')


def success(request):
    return render(request, 'success.html')

