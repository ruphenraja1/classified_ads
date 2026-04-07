import requests
import json

# Sample CSV data for testing
csv_data = """type,Order,Description,LIC,Language,display_name,is_active
City,1,test_city_1,IND,en,Test City 1,true
City,2,test_city_2,IND,en,Test City 2,true
City,3,test_city_3,IND,en,Test City 3,true"""

# Test data structure
test_payload = {
    'csv_data': csv_data
}

# Send request to import endpoint
url = 'http://localhost:8000/employee/lov/import/'
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=test_payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {str(e)}")
