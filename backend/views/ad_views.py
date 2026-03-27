from django.shortcuts import render
from apps.ads.Views_Custom import ad_management, delete_ad

def ad_management_view(request, pk=None):
    return ad_management(request, pk)

def delete_ad_view(request):
    return delete_ad(request)