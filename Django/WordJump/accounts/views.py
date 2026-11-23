from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import SignUpForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('flashcards')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend='django.contrib.auth.backends.ModelBackend',
            )
            messages.success(
                request, f'Welcome to WordJump, {user.username}!'
            )
            return redirect('flashcards')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})
