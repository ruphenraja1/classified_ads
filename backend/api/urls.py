# backend/api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('lov/', views.lov, name='lov'),
    path('users/', views.users, name='users'),
]