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

### Server Interaction ####
        
def send_key_to_server():
    endpoint = f"{SERVER_ADDRESS}/recieve_public_key"
    headers = {'Content-Type': 'application/octet-stream'}
    logger.info("Generating public key")
    key = generate_key()
    payload = pickle.dumps(key)
    
    try:
        logger.info("Sending public key to server")
        response = requests.post(endpoint, data=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logger.info("Key generated and sent successfully to server")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending key to server: {e}")
                                                                            