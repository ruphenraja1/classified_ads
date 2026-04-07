import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ads.models import LOV

# Get all LOV records
all_records = LOV.objects.all().order_by('type', 'language', 'display_name')

print(f"✓ Total LOV Records in Database: {all_records.count()}\n")

# Group by type
type_groups = {}
for lov in all_records:
    if lov.type not in type_groups:
        type_groups[lov.type] = []
    type_groups[lov.type].append(lov)

print("=" * 80)
print("Distribution by Type:")
print("=" * 80)
for ltype in type_groups:
    count = len(type_groups[ltype])
    print(f"  {ltype}: {count} records")

# Show language breakdown for City type
if 'City' in type_groups:
    city_records = type_groups['City']
    lang_counts = {'en': 0, 'ta': 0}
    for lov in city_records:
        if lov.language in lang_counts:
            lang_counts[lov.language] += 1
    
    print(f"\n{'City Type Language Breakdown':=^80}")
    print(f"  English (en): {lang_counts['en']} records")
    print(f"  Tamil (ta): {lang_counts['ta']} records")
    print(f"  Total City: {len(city_records)} records\n")
    
    print(f"{'Sample City Records':=^80}")
    print(f"{'Language':<10} {'Display Name':<30} {'LIC':<10} {'Active':<10}")
    print("-" * 80)
    for lov in city_records[:10]:
        print(f"{lov.language:<10} {lov.display_name:<30} {lov.lic:<10} {str(lov.is_active):<10}")
    
    if len(city_records) > 10:
        print(f"... and {len(city_records) - 10} more City records")
