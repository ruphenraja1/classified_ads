#!/usr/bin/env python
"""Create LOV records for homepage UI strings"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ads.models import LOV

# UI strings for homepage - English and Tamil
ui_strings = [
    # Type, LIC, English, Tamil
    ('UI_HOME', 'SITE_TITLE', 'Daily Classifieds', 'டெய்லி வகைப்படுத்தப்பட்டவை'),
    ('UI_HOME', 'POST_AD_BUTTON', 'Post an Ad', 'விளம்பரம் இடுங்கள்'),
    ('UI_HOME', 'SELECT_CITY_HEADER', 'Select Your City', 'உங்கள் நகரத்தைத் தேர்ந்தெடுக்கவும்'),
    ('UI_HOME', 'BROWSE_CATEGORIES_HEADER', 'Browse Categories', 'வகைகளை உலாவுக'),
    ('UI_HOME', 'ALL_CITIES', 'All Cities', 'அனைத்து நகரங்கள்'),
    ('UI_HOME', 'NO_CITIES_FOUND', 'No cities found', 'நகரங்கள் எதுவும் கிடைக்கவில்லை'),
    ('UI_HOME', 'CITIES_AVAILABLE', 'cities available', 'நகரங்கள் கிடைக்கின்றன'),
    ('UI_HOME', 'POST_YOUR_AD_TODAY', 'Post your ad today', 'இன்றே உங்கள் விளம்பரத்தை இடுங்கள்'),
    ('UI_HOME', 'CITY_SEARCH_PLACEHOLDER', 'Search for your city...', 'உங்கள் நகரத்தைத் தேடுங்கள்...'),
    ('UI_HOME', 'COPYRIGHT_PREFIX', '© 2025 Daily Classifieds', '© 2025 டெய்லி வகைப்படுத்தப்பட்டவை'),
    ('UI_HOME', 'LANGUAGE_EN', 'English', 'English'),
    ('UI_HOME', 'LANGUAGE_TA', 'Tamil', 'தமிழ்'),
]

print("Creating LOV records for UI_HOME strings...")

created_count = 0
for type_name, lic, en_text, ta_text in ui_strings:
    # English record
    en_lov, en_created = LOV.objects.get_or_create(
        type=type_name,
        lic=lic,
        language='en',
        defaults={
            'display_name': lic,
            'description': en_text,
            'order': 1,
            'is_active': True
        }
    )
    if en_created:
        created_count += 1
        print(f"[CREATED] {type_name}/{lic} (en)")
    else:
        # Update if exists
        en_lov.description = en_text
        en_lov.save()
        print(f"[UPDATED] {type_name}/{lic} (en)")
    
    # Tamil record
    ta_lov, ta_created = LOV.objects.get_or_create(
        type=type_name,
        lic=lic,
        language='ta',
        defaults={
            'display_name': lic,
            'description': ta_text,
            'order': 1,
            'is_active': True
        }
    )
    if ta_created:
        created_count += 1
        print(f"[CREATED] {type_name}/{lic} (ta)")
    else:
        # Update if exists
        ta_lov.description = ta_text
        ta_lov.save()
        print(f"[UPDATED] {type_name}/{lic} (ta)")

print(f"\nDone! Total records: {created_count}")
print("\nYou can now fetch these strings using:")
print("  /api/lov/list/?type=UI_HOME&language=en")
print("  /api/lov/list/?type=UI_HOME&language=ta")
