# accounts/urls.py
from django.urls import path
from django.views.generic import TemplateView

from .views import SignUpView
from .views import profile

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("profile/", profile, name='profile')
]
