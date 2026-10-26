from django.shortcuts import render
from .models import Flashcard

def home(request):
    card = Flashcard.objects.order_by('?').first()
    
    context = {
        'heading': "Hello from the Template!",
        'card': card
    }
    return render(request, 'WordJump/home.html', context)
