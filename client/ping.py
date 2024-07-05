import requests

SERVER_ADDRESS = "http://server:5001/"

if __name__=='__main__':
    try:
        response = requests.get(SERVER_ADDRESS)
        if response.status_code == 200:
            print(f"Server is active: {SERVER_ADDRESS}")
        else:
            print(f"Server returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to server: {e}")