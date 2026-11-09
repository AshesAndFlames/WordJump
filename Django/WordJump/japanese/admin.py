
from django.contrib import admin
from .models import Flashcard


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
