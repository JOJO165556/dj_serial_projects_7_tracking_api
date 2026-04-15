from django.urls import path
from .views import UserCreateView, UserListView

urlpatterns = [
    path('create/', UserCreateView.as_view()),
    path('', UserListView.as_view()),
]
