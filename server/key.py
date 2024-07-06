import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
FHE_PUBLIC_KEY_DIR = "./tmp/key.txt"

def write_key(key):
    if not key:
        raise ValueError("Key is empty")
    try:
        with open(FHE_PUBLIC_KEY_DIR, 'w+') as file:
            file.write(key)
    except FileNotFoundError:
        logger.error(f"Key file '{FHE_PUBLIC_KEY_DIR}' not found")
        raise
    except IOError as e:
        logger.error(f"Error reading key file: {e}")
        raise
    
    logger.info("Key written on server")

def ensure_key_exists():
    os.makedirs(os.path.dirname(FHE_PUBLIC_KEY_DIR), exist_ok=True)
    if not os.path.exists(FHE_PUBLIC_KEY_DIR) or os.path.getsize(FHE_PUBLIC_KEY_DIR) == 0:
        logger.error("Key not found!")
        raise FileNotFoundError("Key not found on server-side")

def read_key():
    try:
        with open(FHE_PUBLIC_KEY_DIR, 'r') as file:
            if key := file.read().strip():
                return key
            
            raise ValueError("Key file is empty")
            
    except FileNotFoundError:
        logger.error(f"Key file '{FHE_PUBLIC_KEY_DIR}' not found")
        raise
    except IOError as e:
        logger.error(f"Error reading key file: {e}")
        raise

def get_key():
    ensure_key_exists()
    return read_key()