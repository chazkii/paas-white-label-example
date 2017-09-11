from functools import lru_cache

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.core.mail import send_mail

from whitelabel.models import Profile, Company, CompanyAdmin
from whitelabel.forms import SignUpForm


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
    if request.user.is_authenticated:
        return redirect('home')
    company = Company.objects.get(id=company_id)
    company_name = company.name
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.company = company
            user.save()
            company_admins = CompanyAdmin.objects.filter(company=company).all()
            admins = [u.user for u in company_admins]
            confirm_link = 'http:// %s/confirm/%s/' % (request.get_host(), user.profile.uuid)
            # import ipdb
            # ipdb.set_trace()
            for a in admins:
                params = {
                    'admin': a,
                    'new_user': user,
                    'company': company,
                    'confirm_link': confirm_link
                }
                plain = render_to_string('emails/admin/new-user.txt', params)
                html = render_to_string('emails/admin/new-user.html', params)
                print('Sending a confirm accout email for "%s" to "%s"' % (user.username, a.email))
                send_mail(
                    'New registration email',
                    plain,
                    # 'no-reply@outbound.sendgrid.net',
                    'Charlie Smith <charlie@pensolve.com>',
                    [a.email],
                    html_message=html
                )

            return redirect('success')
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

