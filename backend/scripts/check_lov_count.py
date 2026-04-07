#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ads.models import LOV

# Check initial count
print(f"Initial record count: {LOV.objects.count()}")

# Show the last 5 records
print("\nLast 5 records:")
for lov in LOV.objects.all().order_by('-id')[:5]:
    print(f"  ID: {lov.id}, Type: {lov.type}, LIC: {lov.lic}, Name: {lov.display_name}")
