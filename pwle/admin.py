from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group


class PWLEAdmin(AdminSite):
    site_header = '<Insert company name here> admin'

    def each_context(self, request):
        script_name = request.META['SCRIPT_NAME']
        site_url = script_name if self.site_url == '/' and script_name else self.site_url

        # simply fetch user here and customize 
        group_name = request.user.groups.all()[0].name
        site_title = "%s admin" % group_name

        return {
            'site_title': site_title,
            'site_header': site_title,
            'site_url': site_url,
            'has_permission': self.has_permission(request),
            'available_apps': self.get_app_list(request),
        }


admin_site = PWLEAdmin(name='admin')
admin_site.register(User)
admin_site.register(Group)
