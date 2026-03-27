from django.urls import path
from . import views_new as views
from .lov_detail_api import lov_detail_api

urlpatterns = [
    path('ads/', views.AdListCreate.as_view(), name='ad-list'),
    path('ads/<int:pk>/', views.AdDetail.as_view(), name='ad-detail'),
    path('lov/list/', views.LOVList.as_view(), name='lov-list'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('lov/', views.lov_management, name='lov_management'),
    path('lov/copy/', views.copy_lov, name='copy_lov'),
    path('lov/delete/', views.delete_lov, name='delete_lov'),
    path('lov/import/', views.import_lov, name='import_lov'),
    path('lov/<str:pk>/', views.lov_management, name='lov_management_detail'),
    path('lov/detail/<int:pk>/', lov_detail_api, name='lov_detail_api'),
    path('ad/', views.ad_management, name='ad_management'),
    path('ad/<str:pk>/', views.ad_management, name='ad_management_detail'),
    path('ad/delete/', views.delete_ad, name='delete_ad'),
    path('blockeduser/', views.blockeduser_management, name='blockeduser_management'),
    path('blockeduser/<str:pk>/', views.blockeduser_management, name='blockeduser_management_detail'),
    path('blockeduser/delete/', views.delete_blockeduser, name='delete_blockeduser'),
    path('verify/', views.verify_content, name='verify_content'),
    path('', views.admin_dashboard, name='employee_dashboard_root'),

    
]
