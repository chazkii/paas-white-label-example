from pwle.admin import admin_site

from whitelabel.models import Profile, CompanyAdmin


admin_site.register(Profile)
admin_site.register(CompanyAdmin)
