from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader


def index(request):
    # template = loader.get_template('index.html')
    # return HttpResponse(template.render({}, request))
    return render(
        request,
        'whitelabel/index.html',
        {}
    )
