# Adding email verification per company

## Caveats
* While user registration is done on a per company basis, administration 
  rights of a company admin gives permission to modify the entire database.
  So not production ready.

## Preparation

* You have an existing Django project
* Create a new Django app called `whitelabel` with `python manage.py startapp whitelabel`

### Emailing

1. Sign up for an emailing service. Best I have found so far is [mailgun](http://mailgun.com) 
   as its sandbox offering is performant enough to test the functionality to be implemented.
2. Follow [django-mailgun - Getting going](https://github.com/bradwhittington/django-mailgun/#getting-going)
   instructions.
3. Now you can simply send emails in real time on Django by calling [`send_mail()`](https://docs.djangoproject.com/en/1.11/topics/email/#quick-example).

### Signing up

Our requirements for signup is:
* An anonymous user with any email can signup under a particular company.
* The user will be given an account but will be unable to sign in.
* An admin of that company is sent an email asking to approve the new signup.
* At the click of a link, the admin approves.
* The user will be sent an email confirming the approval and will successfully login in when attempted.

With that in mind, let's start with the models.

`whilelabel/models.py`
```python
import uuid

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Company(models.Model):
    name = models.CharField(max_length=256)
    uiud = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


# This model allows for multiple admins per company
class CompanyAdmin(models.Model):
    company = models.ForeignKey(Company, related_name='+')
    user = models.ForeignKey(User, related_name='+')

    def __str__(self):
        return "%s : %s" % (self.user.username, self.company.name)


# We create a profile model as a non-invasive way of extending the default
# User model. More mentioned in the official docs here:
# https://docs.djangoproject.com/en/1.11/topics/auth/customizing/#extending-the-existing-user-model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, null=True, related_name='+')

    def __str__(self):
        return "%s <%s>" % (self.user.username, self.user.email)


# Leverages [Django signals](https://docs.djangoproject.com/en/1.11/topics/signals)
# to automatically create a profile instance everytime a user instance is created.
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
```

You may notice that we did not create any field for approval. This is because the default Django 
user model has the `is_active` field that we will use. As we are not creating any more models, 
we can run `python manage.py makemigrations` to generate an initial migration.

Let's look at our routing next.

`whitelabel/urls.py`
```python
from django.conf.urls import url
from pwle.admin import admin_site
from django.contrib.auth import views as auth_views
from whitelabel import views as whitelabel_views

# https://stackoverflow.com/questions/11384589/what-is-the-correct-regex-for-matching-values-generated-by-uuid-uuid4-hex
UUID4_REGEX = r'([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})'

urlpatterns = [
    url(r'^admin/', admin_site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^success/$', whitelabel_views.success, name='success'),
    url(r'^signup/%s/$' % UUID4_REGEX, whitelabel_views.signup),
    url(r'^approve/%s/$' % UUID4_REGEX, whitelabel_views.approve_new_account),
    url(r'$', whitelabel_views.index, name='home'),
] 
```

Main things to note here are:
* KISS - use default login and logout views provided by Dango
* `signup/<company_uuid>` - separate endpoint per company
* `approve/<user_uuid>` - HTTP method to approve an account - better than manually doing it in admin panel.
* `UUID4_REGEX` - never use primary keys (at least SQL styled ones) as url entry/query params as
  it is a security hole. Primary key usage means an attacker can simply cycle through integers.
  
Lastly on to the views. We will look at the views one by one in `whitelabel/views.py`:

   
```python
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from django.core.mail import send_mail

from whitelabel.models import Profile, Company, CompanyAdmin
from whitelabel.forms import SignUpForm


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
                # ignore plain for the tutorial, it is there if the email server requests a non HTML version
                plain = render_to_string('emails/admin/new-user.txt', params)
                html = render_to_string('emails/admin/new-user.html', params)
                print('Sending a approve account email for "%s" to "%s"' % (user.username, a.email))
                send_mail(
                    'A new account needs to be approved',
                    plain,
                    'Charlie Smith <charlie@chuckus.nz>',
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
        'Charlie Smith <charlie@chuckus.nz>',
        [new_user_email],
        html_message=html
    )
    return render(request, 'approve.html', {'email': new_user_email})


def success(request):
    return render(request, 'success.html')
```

Each view is pretty self-explanatory. For the `/signup` and `/approve`, we are simply doing 
database operations to save or get data, using the data as params to the template renderers, 
then sending emails, and returning a render response to display in the browser.

Things to note:

* Templates can be fetched from the repo [here](https://github.com/chuckus/paas-white-label-example/tree/master/templates).
  Copy these to `whitelabel/templates`.

* Django does not offer any view module for signing up/creating a user, but does offer a form for 
  creating a user called [UserCreationForm](https://docs.djangoproject.com/en/1.8/topics/auth/default/#django.contrib.auth.forms.UserCreationForm).
  But this form only requires password and username. We need an email to send emails to. So we extend it as follows:
  
  
`whitelabel/forms.py`
```python
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2',)
```

Django will automatically add those extra fields to the form.

### Testing

First, we want to make it easy to test by reducing the number of manual steps. 
We do this by writing a script that autopopulates the database. But how do we 
execute the script in (one of) the Django way(s)? 
By adding [`django-admin commands`](https://docs.djangoproject.com/en/1.11/howto/custom-management-commands/)

`whitelabel/management/commands/populate.py`
```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from whitelabel.models import Company, CompanyAdmin


class Command(BaseCommand):
    help = "Populate database with test data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default=False,
            help="Email to save to all users",
            required=True
        )

    def handle(self, *args, **options):
        email = options['email']
        c, _ = Company.objects.update_or_create(name="Acme")
        u1, _ = User.objects.update_or_create(first_name="Adam",
                                              last_name="Smith",
                                              username='asmith',
                                              is_superuser=True,
                                              is_staff=True,
                                              email=email)
        u1.set_password('password')
        u1.save()
        u1.refresh_from_db()
        u1.profile.company = c
        u1.save()

        CompanyAdmin.objects.update_or_create(user=u1, company=c)

        u2, _ = User.objects.update_or_create(first_name="Bob",
                                              last_name="Smith",
                                              username='bsmith',
                                              is_superuser=False,
                                              is_staff=False,
                                              email=email)
        u2.set_password('password')
        u2.save()
        u2.refresh_from_db()
        u2.profile.company = c
        u2.save()
        print('Added users "asmith" (admin) and "bsmith" with password "password"')
```

Now we can simply run `python manage.py populate --email <your target email>` to populate the tables.
(make sure you have run `python manage.py migrate` to create the tables)

To test locally, simply use `python manage.py runserver`.
