
from django.conf import settings
from django.db import models


class Flashcard(models.Model):

    JLPT_LEVELS = [
        ('N5', 'JLPT N5 - Beginner'),
        ('N4', 'JLPT N4 - Elementary'),
        ('N3', 'JLPT N3 - Intermediate'),
    ]

    foreign_word = models.CharField(
        max_length=100
    )

    translation = models.CharField(
        max_length=255
    )

    part_of_speech = models.CharField(
        max_length=100,
        blank=True
    )

    example_sentence = models.TextField(
        blank=True
    )

    jlpt_level = models.CharField(
        max_length=2,
        choices=JLPT_LEVELS,
        default='N5'
    )

    def __str__(self):
        return f"{self.foreign_word} ({self.jlpt_level})"

    class Meta:
        ordering = ['jlpt_level', 'foreign_word']

        constraints = [
            models.UniqueConstraint(
                fields=['foreign_word', 'jlpt_level'],
                name='unique_word_per_jlpt_level'
            )
        ]


class Answer(models.Model):
    """One self-graded answer: a user flipped a card and said
    whether they knew it. Used to bias which cards come up next."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    flashcard = models.ForeignKey(
        Flashcard,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    was_correct = models.BooleanField()

    answered_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        result = 'correct' if self.was_correct else 'wrong'
        return f"{self.user} - {self.flashcard.foreign_word}: {result}"

    class Meta:
        ordering = ['-answered_at']

        indexes = [
            models.Index(fields=['user', 'flashcard']),
            models.Index(fields=['user', '-answered_at']),
        ]
