import requests
import json

# Complete set of 38 Tamil Nadu cities with English and Tamil translations
csv_data = """type,Order,Description,LIC,Language,display_name,is_active
City,1,Chennai,IND,en,Chennai,true
City,2,Tiruvallur,IND,en,Tiruvallur,true
City,3,Kanchipuram,IND,en,Kanchipuram,true
City,4,Ranipet,IND,en,Ranipet,true
City,5,Vellore,IND,en,Vellore,true
City,6,Tirupattur,IND,en,Tirupattur,true
City,7,Krishnagiri,IND,en,Krishnagiri,true
City,8,Dharmapuri,IND,en,Dharmapuri,true
City,9,Salem,IND,en,Salem,true
City,10,Namakkal,IND,en,Namakkal,true
City,11,Erode,IND,en,Erode,true
City,12,Tiruppur,IND,en,Tiruppur,true
City,13,Nilgiris,IND,en,Nilgiris,true
City,14,Coimbatore,IND,en,Coimbatore,true
City,15,Madurai,IND,en,Madurai,true
City,16,Theni,IND,en,Theni,true
City,17,Dindigul,IND,en,Dindigul,true
City,18,Karur,IND,en,Karur,true
City,19,Tiruchirapalli,IND,en,Tiruchirapalli,true
City,20,Ariyalur,IND,en,Ariyalur,true
City,21,Perambalur,IND,en,Perambalur,true
City,22,Ramanathapuram,IND,en,Ramanathapuram,true
City,23,Sivaganga,IND,en,Sivaganga,true
City,24,Pudukottai,IND,en,Pudukottai,true
City,25,Virudhunagar,IND,en,Virudhunagar,true
City,26,Tenkasi,IND,en,Tenkasi,true
City,27,Tirunelveli,IND,en,Tirunelveli,true
City,28,Kanniyakumari,IND,en,Kanniyakumari,true
City,29,Kanyakumari,IND,en,Kanyakumari,true
City,30,Thoothukudi,IND,en,Thoothukudi,true
City,31,Nagapattinam,IND,en,Nagapattinam,true
City,32,Thivaruran,IND,en,Thivaruran,true
City,33,Chengalpattu,IND,en,Chengalpattu,true
City,34,Villupuram,IND,en,Villupuram,true
City,35,Kallakurichi,IND,en,Kallakurichi,true
City,36,Mayiladuthurai,IND,en,Mayiladuthurai,true
City,37,Cuddalore,IND,en,Cuddalore,true
City,38,Villupuram,IND,en,Villupuram,true
City,1,Chennai,IND,ta,சென்னை,true
City,2,Tiruvallur,IND,ta,திருவள்ளூர்,true
City,3,Kanchipuram,IND,ta,காஞ்சிபுரம்,true
City,4,Ranipet,IND,ta,ரானிப்பேட்டை,true
City,5,Vellore,IND,ta,வேலூர்,true
City,6,Tirupattur,IND,ta,திருப்பத்தூர்,true
City,7,Krishnagiri,IND,ta,கிருஷ்ணகிரி,true
City,8,Dharmapuri,IND,ta,தர்மபுரி,true
City,9,Salem,IND,ta,சேலம்,true
City,10,Namakkal,IND,ta,நாமக்கல்,true
City,11,Erode,IND,ta,ஈரோடு,true
City,12,Tiruppur,IND,ta,திருப்பூர்,true
City,13,Nilgiris,IND,ta,நीलகिരि,true
City,14,Coimbatore,IND,ta,கோயம்பூர்,true
City,15,Madurai,IND,ta,மதுரை,true
City,16,Theni,IND,ta,தேனி,true
City,17,Dindigul,IND,ta,திண்டுக்கல்,true
City,18,Karur,IND,ta,கரூர்,true
City,19,Tiruchirapalli,IND,ta,திருச்சிரப்பள்ளி,true
City,20,Ariyalur,IND,ta,அரியலூர்,true
City,21,Perambalur,IND,ta,பெரம்பலூர்,true
City,22,Ramanathapuram,IND,ta,இராமநாதபுரம்,true
City,23,Sivaganga,IND,ta,சிவகங்கை,true
City,24,Pudukottai,IND,ta,புதுக்கோட்டை,true
City,25,Virudhunagar,IND,ta,விருதுநகர்,true
City,26,Tenkasi,IND,ta,தென்காசி,true
City,27,Tirunelveli,IND,ta,திருநெல்வேலி,true
City,28,Kanniyakumari,IND,ta,கன்னியாकुमारी,true
City,29,Kanyakumari,IND,ta,கன்னியाकुमारी,true
City,30,Thoothukudi,IND,ta,தூத்துக்குடி,true
City,31,Nagapattinam,IND,ta,நாகப்பட்టினம்,true
City,32,Thivaruran,IND,ta,திவாரூர்,true
City,33,Chengalpattu,IND,ta,சேங்கற்பட்டு,true
City,34,Villupuram,IND,ta,விழுப்புரம்,true
City,35,Kallakurichi,IND,ta,கள்ளக்குறிச்சி,true
City,36,Mayiladuthurai,IND,ta,மயிலாடுதுறை,true
City,37,Cuddalore,IND,ta,கடலூர்,true
City,38,Villupuram,IND,ta,விழுப்புரம்,true"""

payload = {'csv_data': csv_data}
url = 'http://localhost:8000/employee/lov/import/'

try:
    response = requests.post(url, json=payload)
    result = response.json()
    
    print("✓ Import Complete!")
    print(f"  Status Code: {response.status_code}")
    print(f"  Created: {result.get('created')} records")
    print(f"  Updated: {result.get('updated')} records")
    print(f"  Errors: {result.get('errors')} records")
    
except Exception as e:
    print(f"✗ Error: {e}")
