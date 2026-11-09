
from django.shortcuts import render
from .models import Flashcard


def flashcards(request):

    level = request.GET.get('level', 'N5').upper()

    valid_levels = ['N5', 'N4', 'N3']

    if level not in valid_levels:
        level = 'N5'

    cards = Flashcard.objects.filter(
        jlpt_level=level
    )

    card = cards.order_by('?').first()

    context = {
        'card': card,
        'selected_level': level,
        'page': 'flashcards',
        'total_words': cards.count(),
    }

    return render(
        request,
        'wordjump.html',
        context
    )
