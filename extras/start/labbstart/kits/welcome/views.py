from django.shortcuts import render


def index(request):
    """Welcome page view"""
    return render(request, "pages/index.html")
