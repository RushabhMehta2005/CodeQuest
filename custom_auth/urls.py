from django.urls import path
from . import views

app_name = "custom_auth"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("edit_password/", views.edit_password, name="edit_password"),
]
