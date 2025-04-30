import requests
from requests.auth import HTTPBasicAuth

# Sentinel Hub credentials
CLIENT_ID = '822fa3a8-c46e-4722-88c2-1a339729ad0b'
SECRET_KEY = 'E8vhdaB1eexDdh1p5HKnFcdZt7ZactTw'
API_URL = 'https://services.sentinel-hub.com/oauth/token'

# Function to get access token
def get_access_token(client_id=CLIENT_ID, secret_key=SECRET_KEY):
    payload = {'grant_type': 'client_credentials'}
    response = requests.post(API_URL, auth=HTTPBasicAuth(client_id, secret_key), data=payload)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        print('Access Token:', access_token)
        return access_token
    else:
        print(f'Failed to obtain access token: {response.status_code} - {response.text}')
        return None

if __name__ == "__main__":
    get_access_token()