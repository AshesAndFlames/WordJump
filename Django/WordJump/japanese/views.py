
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Answer, Flashcard
from .selection import pick_card


VALID_LEVELS = ['N5', 'N4', 'N3']


@login_required
def flashcards(request):

    level = request.GET.get('level', 'N5').upper()

    if level not in VALID_LEVELS:
        level = 'N5'

    cards = Flashcard.objects.filter(
        jlpt_level=level
    )

    card, card_stats = pick_card(request.user, cards)

    context = {
        'card': card,
        'card_stats': card_stats,
        'selected_level': level,
        'page': 'flashcards',
        'total_words': cards.count(),
    }

    return render(
        request,
        'wordjump.html',
        context
    )


@login_required
@require_POST
def record_answer(request):

    card_id = request.POST.get('card_id', '')
    result = request.POST.get('result')

    if not card_id.isdigit() or result not in ('correct', 'wrong'):
        return HttpResponseBadRequest('Invalid answer.')

    card = get_object_or_404(Flashcard, pk=int(card_id))

    Answer.objects.create(
        user=request.user,
        flashcard=card,
        was_correct=(result == 'correct'),
    )

    return redirect(
        f"{reverse('flashcards')}?level={card.jlpt_level}"
    )
