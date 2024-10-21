import requests

# Deribit API URL
BASE_URL = 'https://test.deribit.com/api/v2'

# Your API keys
CLIENT_ID = '9YgyTMFg'  # Replace with your client_id
CLIENT_SECRET = '9xYau6uFd8PWR6iHvQNCNM4mFWl2Pr84wu20lS6NePc'  # Replace with your client_secret

# Function to authenticate and get the access token
def get_auth_token():
    url = f'{BASE_URL}/public/auth'
    
    # Query parameters to be sent in the URL
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    
    # Set headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Send the GET request with params and headers
    response = requests.get(url, headers=headers, params=params)
    
    # Check for valid status
    if response.status_code == 200:
        try:
            result = response.json()  # Parse the JSON response
            print("Access Token:", result['result']['access_token'])
            return result['result']['access_token']
        except ValueError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response: {response.text}")
    else:
        print(f"Failed request with status code {response.status_code}")
        print(f"Response text: {response.text}")

    return -1

# Example usage
#get_auth_token()