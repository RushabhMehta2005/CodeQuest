from django.urls import path
from . import views

app_name = "Quest"
urlpatterns = [
    path("", views.home, name="home"),
    path("problemset/<int:id>/", views.problem_submit, name="problem_submit"),
    path("tags/<int:id>/", views.problem_by_tag, name="problems_by_tag"),
]
