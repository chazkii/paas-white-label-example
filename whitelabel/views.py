from functools import lru_cache

from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group

from whitelabel.models import CompanyStyle


@lru_cache(maxsize=64)
def get_bg_color_from_group(group_id):
    return CompanyStyle.objects.filter(user_group=group_id).first().background_color_hex


def index(request):
    group = request.user.groups.all()[0].id
    bg_color = get_bg_color_from_group(group)
    return render(
        request,
        'whitelabel/index.html',
        {
            "background_color": bg_color
        }
    )


def signup(request, company_id):
    # https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
    company = Group.get(company_id)
    company_name = company.name
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form, 'company_name': company_name})
