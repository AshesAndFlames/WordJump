
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
