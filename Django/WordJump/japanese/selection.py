"""Weighted card selection: words a user gets wrong come up more often."""

import random

from django.db.models import Count, Q

from .models import Answer


# How much each wrong answer boosts a card, relative to an unseen card.
WRONG_WEIGHT = 2.0

# Floor so well-known words still show up occasionally for review.
MIN_WEIGHT = 0.2


def card_weight(correct, wrong):
    """
    Unseen card            -> 1.0
    1 wrong                -> 3.0
    2 wrong                -> 5.0
    1 wrong, then 1 right  -> 1.5
    2 right                -> 0.33
    many right             -> 0.2 (floor)
    """
    return max(MIN_WEIGHT, (1 + WRONG_WEIGHT * wrong) / (1 + correct))


def user_stats(user, cards):
    """{flashcard_id: {'correct': n, 'wrong': n}} for this user's answers."""
    rows = (
        Answer.objects
        .filter(user=user, flashcard__in=cards)
        .values('flashcard')
        .annotate(
            correct=Count('id', filter=Q(was_correct=True)),
            wrong=Count('id', filter=Q(was_correct=False)),
        )
    )
    return {
        row['flashcard']: {'correct': row['correct'], 'wrong': row['wrong']}
        for row in rows
    }


def pick_card(user, cards, rng=random):
    """
    Choose a card from the `cards` queryset, weighted by the user's
    history. Avoids repeating the card they just answered.
    Returns (card, stats_for_card) or (None, None) if there are no cards.
    """
    ids = list(cards.values_list('id', flat=True))
    if not ids:
        return None, None

    stats = user_stats(user, cards)

    last_answered = (
        Answer.objects
        .filter(user=user)
        .order_by('-answered_at', '-id')
        .values_list('flashcard_id', flat=True)
        .first()
    )
    if len(ids) > 1 and last_answered in ids:
        ids.remove(last_answered)

    empty = {'correct': 0, 'wrong': 0}
    weights = [
        card_weight(**stats.get(card_id, empty)) for card_id in ids
    ]

    chosen_id = rng.choices(ids, weights=weights, k=1)[0]
    return cards.get(pk=chosen_id), stats.get(chosen_id, empty)
