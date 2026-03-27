from django.urls import path
from .admin_views import admin_dashboard_view, verify_content_view
from .lov_views import lov_management_view, copy_lov_view, delete_lov_view, import_lov_view
from .ad_views import ad_management_view, delete_ad_view
from .blockeduser_views import blockeduser_management_view, delete_blockeduser_view
from apps.ads.lov_detail_api import lov_detail_api

urlpatterns = [
    path('admin/', admin_dashboard_view, name='admin_dashboard'),
    path('lov/', lov_management_view, name='lov_management'),
    path('lov/copy/', copy_lov_view, name='copy_lov'),
    path('lov/delete/', delete_lov_view, name='delete_lov'),
    path('lov/import/', import_lov_view, name='import_lov'),
    path('lov/<str:pk>/', lov_management_view, name='lov_management_detail'),
    path('lov/detail/<int:pk>/', lov_detail_api, name='lov_detail_api'),
    path('ad/', ad_management_view, name='ad_management'),
    path('ad/<str:pk>/', ad_management_view, name='ad_management_detail'),
    path('ad/delete/', delete_ad_view, name='delete_ad'),
    path('blockeduser/', blockeduser_management_view, name='blockeduser_management'),
    path('blockeduser/<str:pk>/', blockeduser_management_view, name='blockeduser_management_detail'),
    path('blockeduser/delete/', delete_blockeduser_view, name='delete_blockeduser'),
    path('verify/', verify_content_view, name='verify_content'),
    path('', admin_dashboard_view, name='employee_dashboard_root'),
]