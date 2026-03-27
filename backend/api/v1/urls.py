from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ad_viewset, lov_viewset, blockeduser_viewset

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'ads', ad_viewset.AdViewSet, basename='ad')
router.register(r'lov', lov_viewset.LOVViewSet, basename='lov')
router.register(r'blockedusers', blockeduser_viewset.BlockedUserViewSet, basename='blockeduser')

urlpatterns = [
    path('', include(router.urls)),
]