# backend/api/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('lov/', views.lov, name='lov'),
    path('v1/', include('api.v1.urls')),
]