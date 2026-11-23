import random

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Answer, Flashcard
from .selection import MIN_WEIGHT, card_weight, pick_card


class CardWeightTests(TestCase):

    def test_unseen_is_baseline(self):
        self.assertEqual(card_weight(0, 0), 1.0)

    def test_wrong_answers_increase_weight(self):
        self.assertGreater(card_weight(0, 1), card_weight(0, 0))
        self.assertGreater(card_weight(0, 2), card_weight(0, 1))

    def test_correct_answers_decrease_weight_to_floor(self):
        self.assertLess(card_weight(2, 0), 1.0)
        self.assertEqual(card_weight(50, 0), MIN_WEIGHT)


class SelectionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('aiko', password='x')
        self.cards = [
            Flashcard.objects.create(
                foreign_word=f'word{i}', translation=f't{i}', jlpt_level='N5'
            )
            for i in range(5)
        ]
        self.qs = Flashcard.objects.filter(jlpt_level='N5')

    def test_missed_card_comes_up_more_often(self):
        missed = self.cards[0]
        for _ in range(3):
            Answer.objects.create(
                user=self.user, flashcard=missed, was_correct=False
            )
        # Make a different card the most recent answer, so `missed`
        # isn't excluded as "just answered".
        Answer.objects.create(
            user=self.user, flashcard=self.cards[4], was_correct=True
        )

        rng = random.Random(1234)
        picks = [pick_card(self.user, self.qs, rng)[0] for _ in range(400)]
        share = picks.count(missed) / len(picks)

        # Weight 7 vs 1+1+1 for the others (card 4 excluded) -> ~70%.
        self.assertGreater(share, 0.55)

    def test_does_not_repeat_last_answered_card(self):
        last = self.cards[2]
        Answer.objects.create(user=self.user, flashcard=last, was_correct=False)
        rng = random.Random(0)
        for _ in range(100):
            self.assertNotEqual(pick_card(self.user, self.qs, rng)[0], last)

    def test_other_users_answers_do_not_affect_weights(self):
        other = User.objects.create_user('bob', password='x')
        Answer.objects.create(
            user=other, flashcard=self.cards[0], was_correct=False
        )
        _, stats = pick_card(self.user, self.qs.filter(pk=self.cards[0].pk))
        self.assertEqual(stats, {'correct': 0, 'wrong': 0})

    def test_empty_level(self):
        self.assertEqual(
            pick_card(self.user, Flashcard.objects.none()), (None, None)
        )


class RecordAnswerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('aiko', password='x')
        self.card = Flashcard.objects.create(
            foreign_word='猫', translation='cat', jlpt_level='N4'
        )
        self.url = reverse('record_answer')

    def test_requires_login(self):
        response = self.client.post(
            self.url, {'card_id': self.card.pk, 'result': 'wrong'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Answer.objects.count(), 0)

    def test_records_answer_and_returns_to_level(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url, {'card_id': self.card.pk, 'result': 'wrong'}
        )
        self.assertRedirects(response, reverse('flashcards') + '?level=N4')
        answer = Answer.objects.get()
        self.assertEqual(answer.user, self.user)
        self.assertFalse(answer.was_correct)

    def test_rejects_get_and_bad_input(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        for data in (
            {'card_id': self.card.pk, 'result': 'maybe'},
            {'card_id': 'abc', 'result': 'correct'},
            {'result': 'correct'},
        ):
            self.assertEqual(self.client.post(self.url, data).status_code, 400)
        self.assertEqual(
            self.client.post(
                self.url, {'card_id': 99999, 'result': 'correct'}
            ).status_code,
            404,
        )
        self.assertEqual(Answer.objects.count(), 0)

    def test_flashcard_page_shows_missed_badge(self):
        self.client.force_login(self.user)
        Answer.objects.create(user=self.user, flashcard=self.card, was_correct=False)
        Answer.objects.create(user=self.user, flashcard=self.card, was_correct=False)
        response = self.client.get(reverse('flashcards') + '?level=N4')
        self.assertContains(response, 'Missed 2× before')
        self.assertContains(response, 'name="result" value="wrong"')
