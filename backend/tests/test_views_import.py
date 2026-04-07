#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classifieds.settings')
django.setup()

try:
    from ads import views
    print("Successfully imported views")
    
    # List ALL attributes
    all_attrs = dir(views)
    print(f"\nTotal attributes: {len(all_attrs)}")
    print(f"All attributes: {all_attrs}")
    
except Exception as e:
    print(f"Error importing views: {e}")
    import traceback
    traceback.print_exc()

