from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="homepage"),
    path("auth/login", views.login_request, name="login"),
    path("auth/logout", views.logout_request, name="logout"),
    path("auth/signup", views.signup, name="signup"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("project/add", views.add_new_form, name="add_project"),
    path("project/details", views.contrators_form, name="project_details"),
    path("projects/view", views.table_data_view, name="project_view"),
    path("user/profile", views.users_profile_view, name="user_profile"),

]