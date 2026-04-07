import requests
import json

# Test with a single new city to confirm creation capability
test_csv = """type,Order,Description,LIC,Language,display_name,is_active
City,99,Test New City,IND,en,Test New City,true
City,99,Test New City,IND,ta,பரிசோதனை நகரம்,true"""

payload = {'csv_data': test_csv}
url = 'http://localhost:8000/employee/lov/import/'

try:
    response = requests.post(url, json=payload)
    result = response.json()
    
    print("✓ TEST IMPORT RESULT:")
    print(f"  Status: {response.status_code}")
    print(f"  Success: {result.get('success')}")
    print(f"  Created: {result.get('created')} (new records)")
    print(f"  Updated: {result.get('updated')} (existing records)")
    print(f"  Errors: {result.get('errors')}")
    
except Exception as e:
    print(f"✗ Error: {e}")
