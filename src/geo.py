import json
import requests

response = requests.get("http://api.ipstack.com/67.243.240.102?access_key=1e8045f7688859a698512a0abf267f5b")
json_data = json.loads(response.text)
print("hi")
print(json_data["city"])