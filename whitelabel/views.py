from functools import lru_cache

from django.shortcuts import render

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
