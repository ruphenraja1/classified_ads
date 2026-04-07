import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ads.models import LOV

# Get all city LOV records
city_records = LOV.objects.filter(type='City').order_by('language', 'lic')

print(f"Total City LOV Records: {city_records.count()}\n")
print("Sample Records (showing first 10):")
print("-" * 80)
print(f"{'Type':<10} {'LIC':<10} {'Language':<10} {'Display Name':<20} {'Is Active':<10}")
print("-" * 80)

for lov in city_records[:10]:
    print(f"{lov.type:<10} {lov.lic:<10} {lov.language:<10} {lov.display_name:<20} {str(lov.is_active):<10}")

# Summary by language
print("\n" + "=" * 80)
print("Summary by Language:")
print("=" * 80)
for lang in ['ta', 'en']:
    count = LOV.objects.filter(type='City', language=lang).count()
    print(f"  {lang.upper()}: {count} records")
