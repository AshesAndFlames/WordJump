
from django.urls import path
from . import views


urlpatterns = [
    path(
        '',
        views.flashcards,
        name='flashcards'
    ),
    path(
        'answer/',
        views.record_answer,
        name='record_answer'
    ),
]
