
from django.contrib import admin
from .models import Answer, Flashcard


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):

    list_display = (
        'foreign_word',
        'translation',
        'part_of_speech',
        'jlpt_level',
    )

    list_filter = (
        'jlpt_level',
        'part_of_speech',
    )

    search_fields = (
        'foreign_word',
        'translation',
    )

    ordering = (
        'jlpt_level',
        'foreign_word',
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'flashcard',
        'was_correct',
        'answered_at',
    )

    list_filter = (
        'was_correct',
        'flashcard__jlpt_level',
        'user',
    )

    search_fields = (
        'user__username',
        'flashcard__foreign_word',
    )
