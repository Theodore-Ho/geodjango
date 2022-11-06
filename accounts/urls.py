# accounts/urls.py
from django.urls import path

from .views import SignUpView, profile, change_password

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", profile, name='profile'),
    path("password/", change_password, name='password')
]
