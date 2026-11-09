
from django.shortcuts import render


def home(request):
    return render(
        request,
        'wordjump.html',
        {
            'card': None,
            'selected_level': 'N5',
            'page': 'home',
        }
    )
