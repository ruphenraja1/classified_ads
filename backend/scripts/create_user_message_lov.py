#!/usr/bin/env python
"""Create LOV records for the "when city not found" user message"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ads.models import LOV

# English message
english_msg = 'If your city is not in the list, please select the nearest district name from the dropdown above, and mention your exact city/village name in the Location/Address field below.'

# Tamil message
tamil_msg = 'உங்கள் நகரம் பட்டியலில் இல்லை என்றால், மேலே உள்ள கீழ்தோன்றலில் இருந்து அருகிலுள்ள மாவட்டத்தைத் தேர்ந்தெடுக்கவும், மேலும் உங்கள் சரியான நகரம்/கிராமத்தின் பெயரை கீழே உள்ள இடம்/முகவரி புலத்தில் குறிப்பிடவும்.'

print("Creating LOV records for USER_MSG_1 / WHEN_NO_CITY...")

# Create English record
en_lov, en_created = LOV.objects.get_or_create(
    type='USER_MSG_1',
    lic='WHEN_NO_CITY',
    language='en',
    defaults={
        'display_name': 'WHEN_NO_CITY',
        'description': english_msg,
        'order': 1,
        'is_active': True
    }
)

if en_created:
    print(f"[CREATED] English record")
else:
    # Update if exists
    en_lov.description = english_msg
    en_lov.save()
    print(f"[UPDATED] English record")

# Create Tamil record
ta_lov, ta_created = LOV.objects.get_or_create(
    type='USER_MSG_1',
    lic='WHEN_NO_CITY',
    language='ta',
    defaults={
        'display_name': 'WHEN_NO_CITY',
        'description': tamil_msg,
        'order': 1,
        'is_active': True
    }
)

if ta_created:
    print(f"[CREATED] Tamil record")
else:
    # Update if exists
    ta_lov.description = tamil_msg
    ta_lov.save()
    print(f"[UPDATED] Tamil record")

print("\nDone! LOV records:")
print(f"  Type: USER_MSG_1")
print(f"  LIC: WHEN_NO_CITY")
print(f"  Languages: en, ta")
print(f"\nYou can now fetch this message using:")
print(f"  /api/lov/list/?type=USER_MSG_1&lic=WHEN_NO_CITY&language=en")
print(f"  /api/lov/list/?type=USER_MSG_1&lic=WHEN_NO_CITY&language=ta")
