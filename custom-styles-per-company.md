# Custom stying for admin panel per company

## Preparation

* You have an existing Django project
* Create a new Django app called `whitelabel` with `python manage.py startapp whitelabel`
* You've foldering the "Adding email verification per company" tutorial, specifically, 
  adding the custom models.

## Design

* KISS - admin panel styling for a particular company does not change frequently


## Implementation

### Styling

Luckily, Django makes this easy for us, by making [the admin panel customizable out of the box](https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#set-up-your-projects-admin-template-directories).

As we need to change styling for all admin pages, we will extend the base template.
Looking in `<your virtualenv or global python installation location>/lib/python3.4/site-packages/django/admin/templates/admin` 
we can see there is a `base_site.html` template.

Create a new folder `<PROJECT_ROOT: note this is not the app root>/template/admin/`  and create the file below (we 
are replacing the old template)

`templates/admin/base_site.html`
```html
{% extends "admin/base.html" %}
{% load static from staticfiles %} # This might be just {% load static %} in your ENV

{% block title %}{{ title }} | {{ site_title|default:_('Django site admin') }}{% endblock %}

{% block extrastyle %}
  {{ block.super }}
  {% if request.user.is_authenticated %}
  {% with 'css/'|add:request.user.profile.company.name|add:'-extra.css' as company_css %}
  <link rel="stylesheet" type="text/css" href="{% static company_css %}" />
  {% endwith %}
  {% endif %}
{% endblock %}

{% block branding %}
<h1 id="site-name"><a href="{% url 'admin:index' %}">{{ site_header|default:_('PaaS admin') }}</a></h1>
{% endblock %}

{% block nav-global %}{% endblock %}
```

There is only 4 lines of extra code here, which is the addition of 
a stylesheet linking. It is pretty self explanatory, but very simple to 
manage. Ensure in your in one of your `STATICFILES_DIRS`, that you have a 
`css/Acme-extra.css` (or choose your own company name if not using the 
populating script from the last tutorial)

By default, your production environment should not allow a file listing on the 
`/static` dir so using the `company.name` is fine. But if you want to be more 
secure, you could replace `company.name` with `company.uuid` but the CSS file 
names will not be intuitive anymore.

That's it pretty much! But we just need a little bit more customisation to
make it feel like it is proper admin page for a particular company.

### Naming

What you'll realise is that it will still say `Django administration` as the title 
etc. This can be easily overridden. Simply add the following file:

`<project_name/admin.py`
```python

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User

class PWLEAdmin(AdminSite):
    site_header = '<Insert company name here> admin'

    def each_context(self, request):
        script_name = request.META['SCRIPT_NAME']
        site_url = script_name if self.site_url == '/' and script_name else self.site_url

        # simply fetch user here and customize
        if request.user.is_authenticated:
            company_name = request.user.profile.company.name
            site_title = "%s admin" % company_name
        else:
            site_title = 'PaaS admin panel'

        return {
            'site_title': site_title,
            'site_header': site_title,
            'site_url': site_url,
            'has_permission': self.has_permission(request),
            'available_apps': self.get_app_list(request),
        }


admin_site = PWLEAdmin(name='admin')
admin_site.register(User)
```

The offical Django reference is [here](https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#django.contrib.admin.AdminSite).
Again, very self explanatory if we consider there is only 5 custom lines of code, 
which is to do with the setting of the `site_title` variable, everything else is copied 
from the original implementation of `AdminSite`.
