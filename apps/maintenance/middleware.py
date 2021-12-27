from django.shortcuts import render
from django.conf import settings


class UnderConstructionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.UNDER_CONSTRUCTION:
            return render(request, 'index2.html')
        return self.get_response(request)