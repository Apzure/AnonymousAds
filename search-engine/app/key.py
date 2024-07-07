import os
import requests
import json
import logging
import pickle
from app.process_search_history import generate_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SERVER_ADDRESS = "http://server:5001/"
KEY_FILENAME = "./tmp/key.txt"
FLAG_FILENAME = "./tmp/key_sent.flag"
KEYWORDS_FILENAME = "./tmp/keywords.txt"

### Key operations ###

def ensure_key_exists():
    os.makedirs(os.path.dirname(KEY_FILENAME), exist_ok=True)
    if not os.path.exists(KEY_FILENAME) or os.path.getsize(KEY_FILENAME) == 0:
        key = generate_key()
        with open(KEY_FILENAME, 'wb') as file:
            pickle.dump(key, file)
        logger.info(f"Key file '{KEY_FILENAME}' has been created and written to.")

def read_key():
    try:
        with open(KEY_FILENAME, 'rb') as file:
            if key := pickle.load(file):
                return key
            else:
                raise ValueError("Key file is empty")
    except FileNotFoundError:
        logger.error(f"Key file '{KEY_FILENAME}' not found")
        raise
    except IOError as e:
        logger.error(f"Error reading key file: {e}")
        raise

def get_key():
    ensure_key_exists()
    return read_key()

def is_key_sent():
    return os.path.exists(FLAG_FILENAME)

def mark_key_as_sent():
    with open(FLAG_FILENAME, 'w') as file:
        file.write("sent")
        
### Server Interaction ####
        
def send_key_to_server(key):
    endpoint = f"{SERVER_ADDRESS}/recieve_public_key"
    headers = {'Content-Type': 'application/octet-stream'}
    payload = pickle.dumps(key)
    
    try:
        response = requests.post(endpoint, data=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logger.info(f"Server response: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending key to server: {e}")
        return False
    
def send_key_to_server_if_not_sent():
    if is_key_sent():
        logger.info("Key has already been sent. Skipping.")
        return
    
    key = get_key()
    
    if send_key_to_server(key):
        mark_key_as_sent()
        logger.info("Key sent successfully and marked as sent.")
    else:
        logger.error("Failed to send key to server!")
        raise Exception("Failed to send key to server!")
    