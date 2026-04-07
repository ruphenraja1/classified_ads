#!/usr/bin/env python
"""Insert new cities into LOV table with English and Tamil names"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ads.models import LOV

# List of cities with English and Tamil names
cities = [
    ('Pollachi', 'பொள்ளாச்சி'),
    ('Karaikudi', 'காரைக்குடி'),
    ('Kovilpatti', 'கோவில்பட்டி'),
    ('Palani', 'பழனி'),
    ('Udumalpet', 'உடுமலைப்பேட்டை'),
    ('Gobichettipalayam', 'கோபிசெட்டிபாளையம்'),
    ('Mettupalayam', 'மேட்டுப்பாளையம்'),
    ('Rajapalayam', 'ராஜபாளையம்'),
    ('Sivakasi', 'சிவகாசி'),
    ('Aruppukkottai', 'அருப்புக்கோட்டை'),
    ('Avinashi', 'அவிநாசி'),
    ('Palladam', 'பல்லடம்'),
    ('Dharapuram', 'தரபுரம்'),
    ('Oddanchatram', 'ஒட்டன்சத்திரம்'),
    ('Nilakottai', 'நிலக்கோட்டை'),
    ('Paramakudi', 'பரமக்குடி'),
    ('Devakottai', 'தேவகோட்டை'),
    ('Ambur', 'ஆம்பூர்'),
    ('Vaniyambadi', 'வாணியம்பாடி'),
]

# Get current max order for CITY type
city_lovs = LOV.objects.filter(type='CITY', language='en')
if city_lovs.exists():
    max_order = city_lovs.order_by('-order').first().order
else:
    max_order = 0

print(f"Current max order: {max_order}")
print(f"Inserting {len(cities)} new cities...")

for i, (english_name, tamil_name) in enumerate(cities, start=1):
    order = max_order + i
    lic = english_name.upper().replace(' ', '')
    
    # Create English entry
    en_lov, en_created = LOV.objects.get_or_create(
        type='CITY',
        lic=lic,
        language='en',
        defaults={
            'display_name': english_name,
            'order': order,
            'is_active': True,
            'description': ''
        }
    )
    
    # Create Tamil entry
    ta_lov, ta_created = LOV.objects.get_or_create(
        type='CITY',
        lic=lic,
        language='ta',
        defaults={
            'display_name': tamil_name,
            'order': order,
            'is_active': True,
            'description': ''
        }
    )
    
    if en_created or ta_created:
        print(f"[OK] {english_name} (order: {order})")
    else:
        print(f"[SKIP] {english_name} already exists")

print(f"\nDone! Total cities now: {LOV.objects.filter(type='CITY', language='en').count()}")
