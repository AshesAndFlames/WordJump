from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name='login',
    ),
    # Django's built-in views: logout, password_change(_done),
    # password_reset(_done), password_reset_confirm, password_reset_complete
    path('', include('django.contrib.auth.urls')),
]
