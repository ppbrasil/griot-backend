import requests

base_url = "http://127.0.0.1:8000/api/"
path = "user/auth/"

url = base_url+path

# Get user input
username = input("Enter a username: ")
password = input("Enter a password: ")

data = {
    'username': username,
    'password': password,
}

response = requests.post(url, data=data)

print(f'Respose Code: {response.status_code}')
print(f'Respose Json: {response.json()}')