import csv
from io import StringIO
from django.core.management.base import BaseCommand
from ads.models import LOV


class Command(BaseCommand):
    help = 'Import LOV records from CSV data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            type=str,
            help='CSV data string to import',
        )

    def handle(self, *args, **options):
        # CSV data with all the city records (Tamil and English)
        csv_data = """type,Order,Description,LIC,Language,display_name,is_active
CITY,1,1,CHENNAI,ta,சென்னை,true
CITY,2,2,COIMBATORE,ta,கோயம்புத்தூர்,true
CITY,3,3,TIRUPPUR,ta,திருப்பூர்,true
CITY,4,4,MADURAI,ta,மதுரை,true
CITY,5,5,TIRUCHIRAPPALLI,ta,திருச்சிராப்பள்ளி,true
CITY,6,6,KANCHIPURAM,ta,காஞ்சிபுரம்,true
CITY,7,7,SALEM,ta,சேலம்,true
CITY,8,8,ERODE,ta,ஈரோடு,true
CITY,9,9,VELLORE,ta,வேலூர்,true
CITY,10,10,THOOTHUKUDI,ta,தூத்துக்குடி,true
CITY,11,11,KANYAKUMARI,ta,கன்னியாகுமரி,true
CITY,12,12,CHENGALPATTU,ta,செங்கல்பட்டு,true
CITY,13,13,TIRUVALLUR,ta,திருவள்ளூர்,true
CITY,14,14,VIRUDHUNAGAR,ta,விருதுநகர்,true
CITY,15,15,KARUR,ta,கரூர்,true
CITY,16,16,NAMAKKAL,ta,நாமக்கல்,true
CITY,17,17,KRISHNAGIRI,ta,கிருஷ்ணகிரி,true
CITY,18,18,TIRUNELVELI,ta,திருநெல்வேலி,true
CITY,19,19,THE_NILGIRIS,ta,நீலகிரி,true
CITY,20,20,THANJAVUR,ta,தஞ்சாவூர்,true
CITY,21,21,DINDIGUL,ta,திண்டுக்கல்,true
CITY,22,22,VILLUPURAM,ta,விழுப்புரம்,true
CITY,23,23,TIRUVANNAMALAI,ta,திருவண்ணாமலை,true
CITY,24,24,RANIPET,ta,இராணிப்பேட்டை,true
CITY,25,25,CUDDALORE,ta,கடலூர்,true
CITY,26,26,NAGAPATTINAM,ta,நாகப்பட்டினம்,true
CITY,27,27,THENI,ta,தேனி,true
CITY,28,28,DHARMAPURI,ta,தருமபுரி,true
CITY,29,29,PUDUKKOTTAI,ta,புதுக்கோட்டை,true
CITY,30,30,RAMANATHAPURAM,ta,இராமநாதபுரம்,true
CITY,31,31,SIVAGANGA,ta,சிவகங்கை,true
CITY,32,32,THIRUVARUR,ta,திருவாரூர்,true
CITY,33,33,TENKASI,ta,தென்காசி,true
CITY,34,34,MAYILADUTHURAI,ta,மயிலாடுதுறை,true
CITY,35,35,KALLAKURICHI,ta,கள்ளக்குறிச்சி,true
CITY,36,36,TIRUPATTUR,ta,திருப்பத்தூர்,true
CITY,37,37,ARIYALUR,ta,அரியலூர்,true
CITY,38,38,PERAMBALUR,ta,பெரம்பலூர்,true
CITY,1,1,CHENNAI,en,Chennai,true
CITY,2,2,COIMBATORE,en,Coimbatore,true
CITY,3,3,TIRUPPUR,en,Tiruppur,true
CITY,4,4,MADURAI,en,Madurai,true
CITY,5,5,TIRUCHIRAPPALLI,en,Tiruchirappalli,true
CITY,6,6,KANCHIPURAM,en,Kanchipuram,true
CITY,7,7,SALEM,en,Salem,true
CITY,8,8,ERODE,en,Erode,true
CITY,9,9,VELLORE,en,Vellore,true
CITY,10,10,THOOTHUKUDI,en,Thoothukudi,true
CITY,11,11,KANYAKUMARI,en,Kanyakumari,true
CITY,12,12,CHENGALPATTU,en,Chengalpattu,true
CITY,13,13,TIRUVALLUR,en,Tiruvallur,true
CITY,14,14,VIRUDHUNAGAR,en,Virudhunagar,true
CITY,15,15,KARUR,en,Karur,true
CITY,16,16,NAMAKKAL,en,Namakkal,true
CITY,17,17,KRISHNAGIRI,en,Krishnagiri,true
CITY,18,18,TIRUNELVELI,en,Tirunelveli,true
CITY,19,19,THE NILGIRIS,en,The Nilgiris,true
CITY,20,20,THANJAVUR,en,Thanjavur,true
CITY,21,21,DINDIGUL,en,Dindigul,true
CITY,22,22,VILLUPURAM,en,Villupuram,true
CITY,23,23,TIRUVANNAMALAI,en,Tiruvannamalai,true
CITY,24,24,RANIPET,en,Ranipet,true
CITY,25,25,CUDDALORE,en,Cuddalore,true
CITY,26,26,NAGAPATTINAM,en,Nagapattinam,true
CITY,27,27,THENI,en,Theni,true
CITY,28,28,DHARMAPURI,en,Dharmapuri,true
CITY,29,29,PUDUKKOTTAI,en,Pudukkottai,true
CITY,30,30,RAMANATHAPURAM,en,Ramanathapuram,true
CITY,31,31,SIVAGANGA,en,Sivaganga,true
CITY,32,32,THIRUVARUR,en,Thiruvarur,true
CITY,33,33,TENKASI,en,Tenkasi,true
CITY,34,34,MAYILADUTHURAI,en,Mayiladuthurai,true
CITY,35,35,KALLAKURICHI,en,Kallakurichi,true
CITY,36,36,TIRUPATTUR,en,Tirupattur,true
CITY,37,37,ARIYALUR,en,Ariyalur,true
CITY,38,38,PERAMBALUR,en,Perambalur,true"""

        # Parse CSV
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        
        created_count = 0
        updated_count = 0
        
        for row in reader:
            # Convert 'true'/'false' string to boolean
            is_active = row['is_active'].lower() == 'true'
            
            # Upsert: use update_or_create for idempotent behavior
            lov, created = LOV.objects.update_or_create(
                type=row['type'],
                lic=row['LIC'],
                language=row['Language'],
                defaults={
                    'display_name': row['display_name'],
                    'description': row['Description'],
                    'is_active': is_active,
                    'order': int(row['Order'])
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {lov.type} - {lov.lic} ({lov.language}) - {lov.display_name}"
                    )
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated: {lov.type} - {lov.lic} ({lov.language}) - {lov.display_name}"
                    )
                )
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Upsert completed!\n"
                f"  Created: {created_count} records\n"
                f"  Updated: {updated_count} records"
            )
        )
