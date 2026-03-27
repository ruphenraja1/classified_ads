from django.shortcuts import render
from apps.ads.Views_Custom import admin_dashboard, verify_content

def admin_dashboard_view(request):
    return admin_dashboard(request)

def verify_content_view(request):
    return verify_content(request)