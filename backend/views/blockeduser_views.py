from django.shortcuts import render
from apps.ads.Views_Custom import blockeduser_management, delete_blockeduser

def blockeduser_management_view(request, pk=None):
    return blockeduser_management(request, pk)

def delete_blockeduser_view(request):
    return delete_blockeduser(request)