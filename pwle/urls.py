"""pwle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from pwle.admin import admin_site
from django.contrib.auth import views as auth_views
from whitelabel import views as whitelabel_views
from django.conf.urls.static import static
from django.conf import settings

# https://stackoverflow.com/questions/11384589/what-is-the-correct-regex-for-matching-values-generated-by-uuid-uuid4-hex
UUID4_REGEX = r'([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})'

urlpatterns = [
    url(r'^admin/', admin_site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^signup/([0-9])/$', whitelabel_views.signup),
    url(r'^success/$', whitelabel_views.success, name='success'),
    url(r'^approve/%s/$' % UUID4_REGEX, whitelabel_views.approve_new_account),
    url(r'$', whitelabel_views.index, name='home'),
    # https://docs.djangoproject.com/en/1.11/howto/static-files/#serving-static-files-during-development
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
