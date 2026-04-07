#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classifieds.settings')
django.setup()

# Now try to import
try:
    from ads import views
    print("Views module imported successfully")
    print("\nAvailable functions/classes:")
    for item in dir(views):
        if not item.startswith('_'):
            print(f"  - {item}")
    
    print("\n\nLooking for import_lov specifically:")
    if hasattr(views, 'import_lov'):
        print("  ✓ import_lov found!")
    else:
        print("  ✗ import_lov NOT found!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
