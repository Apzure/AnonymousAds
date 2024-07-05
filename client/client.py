from flask import Flask, request, jsonify
import requests
import time


SERVER_ADDRESS = "http://localhost:5001"

def create_app():
    app = Flask(__name__)
    
    with app.app_context():
        # SHOULD CHECK IF SERVER IS UP
        pass
    
    return app

app = create_app()

def generate_keys():
    return "KEY HERE"

@app.route('/', methods=["GET"])
def send_public_key():
    #Initial Request
    data = {"public_key": generate_keys()}
    response = requests.post('http://localhost:5001/public_key', json=data)
    return jsonify({"status": "sent", "server_response": response.json()})

def ping_server():
    try:
        response = requests.get(SERVER_ADDRESS)
        if response.status_code == 200:
            print(f"Server is active: {SERVER_ADDRESS}")
            return True
        else:
            print(f"Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to server: {e}")
        return False
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
