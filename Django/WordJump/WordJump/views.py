from django.shortcuts import render

def home(request):
    context = {
        'heading': "Hello from the Template!"
    }
    return render(request, 'WordJump/home.html', context)
