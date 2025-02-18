from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="homepage"),
    path("auth/login", views.login_request, name="login"),
    path("auth/logout", views.logout_request, name="logout"),
    path("auth/signup", views.signup, name="signup"),
]