import requests

base_url = "http://127.0.0.1:8000/api/"
path = "user/logout/"

url = base_url+path

token = '32255a358e27cba793366b34931a55aca095e39e'

header = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=header)

print(f'Respose Code: {response.status_code}')
print(f'Respose Json: {response.json()}')