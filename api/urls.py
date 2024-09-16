from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'problems', views.ProblemViewSet)


app_name = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('problems/<int:pk>/submissions/<int:user>/', views.ProblemSubmissionsView.as_view(), name='problem-submissions'),
]