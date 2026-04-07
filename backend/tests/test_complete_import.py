import requests
import json

# Comprehensive test with sample Tamil and English data
tamil_english_data = """type,Order,Description,LIC,Language,display_name,is_active
City,1,Chennai City,IND,ta,சென்னை,true
City,2,Coimbatore City,IND,ta,கோயம்பூர்,true
City,3,Madurai City,IND,ta,மதுரை,true
City,1,Chennai City,IND,en,Chennai,true
City,2,Coimbatore City,IND,en,Coimbatore,true
City,3,Madurai City,IND,en,Madurai,true"""

payload = {
    'csv_data': tamil_english_data
}

url = 'http://localhost:8000/employee/lov/import/'
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"✓ API Status Code: {response.status_code}")
    result = response.json()
    print(f"✓ Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print(f"\n✓ Import Successful!")
        print(f"  - Created: {result.get('created')} new records")
        print(f"  - Updated: {result.get('updated')} existing records")
        print(f"  - Errors: {result.get('errors')} failed records")
    else:
        print(f"✗ Import Failed: {result.get('error')}")
        
except Exception as e:
    print(f"✗ Error: {str(e)}")
