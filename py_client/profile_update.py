import requests, json

id = 1

base_url = "http://127.0.0.1:8000/api/"
path = f"profile/update/{id}/"

url = base_url+path

token = '32255a358e27cba793366b34931a55aca095e39e'

header = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

name = 'Pedro Paulo'
middle_name = 'Brasil'
last_name = 'de Assis Ribeiro'
birth_date = '1980-12-16'
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
