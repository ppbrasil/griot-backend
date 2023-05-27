import requests, json

id = 1

base_url = "http://127.0.0.1:8000/api/"
path = f"profile/update/{id}/"

url = base_url+path

token = '293bc50f57945dd4d7c73079918b4f203b00b53f'

header = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

name = 'Pedro P'
middle_name = 'Brazil'
last_name = 'de Assis Ribeiro'
birth_date = '1980-12-18'
gender = 'male'

data = {
    'name': name,
    'middle_name': middle_name,
    'last_name': last_name,
    'birth_date': birth_date,
    'gender': gender,
}

response = requests.patch(url, headers=header, data=json.dumps(data))

print(f'Respose Code: {response.status_code}')
