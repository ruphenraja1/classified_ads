#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ads.models import LOV

# Create test records
for i in range(3):
    obj, created = LOV.objects.get_or_create(
        type='TEST_TYPE_' + str(i),
        lic='LIC_' + str(i),
        defaults={
            'display_name': f'Test Record {i}',
            'language': 'en',
            'order': i,
            'is_active': True
        }
    )
    if created:
        print(f'Created: {obj.id} - {obj.type}')
    else:
        print(f'Already exists: {obj.id} - {obj.type}')

print(f'\nTotal records: {LOV.objects.count()}')
for lov in LOV.objects.all()[:5]:
    print(f'ID: {lov.id}, Type: {lov.type}, LIC: {lov.lic}, Name: {lov.display_name}')
