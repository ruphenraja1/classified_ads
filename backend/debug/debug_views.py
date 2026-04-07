#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classifieds.settings')
django.setup()

from ads import views

# Check if import_lov exists
print(f"import_lov exists: {hasattr(views, 'import_lov')}")

# List what functions are actually available
print("\nAvailable functions:")
for attr in dir(views):
    if not attr.startswith('_') and callable(getattr(views, attr)):
        print(f"  - {attr}")

