from django.shortcuts import render
from apps.ads.Views_Custom import lov_management, copy_lov, delete_lov, import_lov

def lov_management_view(request, pk=None):
    return lov_management(request, pk)

def copy_lov_view(request):
    return copy_lov(request)

def delete_lov_view(request):
    return delete_lov(request)

def import_lov_view(request):
    return import_lov(request)