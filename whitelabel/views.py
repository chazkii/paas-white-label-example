from functools import lru_cache

from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
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


def signup(request, company_uuid):
    # https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
    if request.user.is_authenticated:
        return redirect('home')
    company = Company.objects.get(uuid=company_uuid)
    company_name = company.name
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.company = company
            user.is_active = False
            user.save()
            company_admins = CompanyAdmin.objects.filter(company=company).all()
            admins = [u.user for u in company_admins]
            approv_link = 'http://%s/approve/%s/' % (request.get_host(), user.profile.uuid)
            for a in admins:
                params = {
                    'admin': a,
                    'new_user': user,
                    'company': company,
                    'approv_link': approv_link
                }
                plain = render_to_string('emails/admin/new-user.txt', params)
                html = render_to_string('emails/admin/new-user.html', params)
                print('Sending a approve account email for "%s" to "%s"' % (user.username, a.email))
                send_mail(
                    'A new account needs to be approved',
                    plain,
                    'Charlie Smith <charlie@pensolve.com>',
                    [a.email],
                    html_message=html
                )

            return redirect('success')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'company_name': company_name})


def approve_new_account(request, user_uuid):
    if not request.user.is_authenticated:
        return redirect('login')
    new_user_profile = Profile.objects.get(uuid=user_uuid)
    new_user_email = new_user_profile.user.email
    # prevent anonymous and normal users from approving
    if request.user.profile.company_id != new_user_profile.company_id \
            or not request.user.is_superuser:
        return HttpResponseForbidden('Forbidden')
    new_user_profile.user.is_active = True
    new_user_profile.user.save()
    params = {
        'email': new_user_email,
        'login_link': 'http://%s/login/' % request.get_host()
    }
    plain = render_to_string('emails/user/approved-user.txt', params)
    html = render_to_string('emails/user/approved-user.html', params)
    send_mail(
        'Your new account is ready to use',
        plain,
        'Charlie Smith <charlie@pensolve.com>',
        [new_user_email],
        html_message=html
    )
    return render(request, 'approve.html', {'email': new_user_email})


def success(request):
    return render(request, 'success.html')

