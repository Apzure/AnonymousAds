from concrete.ml.deployment import FHEModelClient
import numpy as np
from collections import Counter
import re
from sklearn.preprocessing import normalize
from nltk.stem.porter import PorterStemmer
import os
import shutil
import requests
import json
import base64
import logging 
from .predict import get_new_prediction, display_predictions, clean_normalize_predictions
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KEYWORDS_FILENAME = "./tmp/keywords.txt"
STEMMED_KEYWORDS_FILENAME = "./tmp/stemmed_keywords.json"
SERVER_ADDRESS = "http://server:5001/"
FHE_FILE_PATH = "./fhe"

REGEX = re.compile('[^a-zA-Z ]')
STEMMER = PorterStemmer()
client = FHEModelClient(path_dir=FHE_FILE_PATH)

def clear_directory(directory_path):
    try:
        # Ensure the directory exists
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory '{directory_path}' not found")
        
        # Iterate over all the files in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            logger.info("%s", file_path)
            try:
                # Check if it is a file (not a directory) and remove it
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    
                # If it's a directory, you can decide whether to delete it
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        logger.info(f"Directory '{directory_path}' has been cleared.")
    except Exception as e:
        print(f"Error clearing directory: {e}")



generate_key = lambda: client.get_serialized_evaluation_keys()
serialized_evaluation_keys = generate_key()


def init_keywords():
    get_keywords_if_not_got()
    process_keywords()
    
def is_keywords_got():
    return os.path.exists(KEYWORDS_FILENAME)
    
def get_keywords_if_not_got():
    if is_keywords_got():
        logger.info("Keywords have already been retrieved. Skipping.")
        logger.info("-" * 30)  
        return

    endpoint = f"{SERVER_ADDRESS}/get_keywords"
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            keywords = response.json().get("keywords")
            logger.info("Received keywords from server: %s", keywords)

            os.makedirs(os.path.dirname(KEYWORDS_FILENAME), exist_ok=True)
            with open(KEYWORDS_FILENAME, 'w') as file:
                json.dump(keywords, file)
            logger.info(f"Keywords file '{KEYWORDS_FILENAME}' has been created and written to.")
            logger.info("-" * 30)  
        else:
            logger.warning(f"Server returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to server: {e}")
        
def process_keywords():
    logger.info("Starting to process keywords into stemmed_keywords")
    with open(KEYWORDS_FILENAME, 'r') as file:
        keywords = json.load(file)
    stemmed_keywords = list(map(STEMMER.stem, keywords))
    logger.info("Stemmed_keywords have been processed: %s", stemmed_keywords)
    with open(STEMMED_KEYWORDS_FILENAME, 'w') as file:
        json.dump(stemmed_keywords, file)
    logger.info(f"Stemmed Keywords file '{STEMMED_KEYWORDS_FILENAME}' has been created and written to.")    
    logger.info("Succesfully processed keywords into stemmed_keywords")
    logger.info("-" * 30)  

# Converts search history to encrypted normalized vector
def process_search_history(search_history): 
    try:
        logger.info("-" * 30)  
        logger.info("Starting to process search history with %d entries", len(search_history))
        text = " ".join(search_history)
        
        with open(STEMMED_KEYWORDS_FILENAME, 'r') as file:
            stemmed_keywords = json.load(file)
        logger.info("Retrieved %d stemmed keywords from file", len(stemmed_keywords))
        
        logger.debug("Preprocessing text: removing hyphens, applying regex, and converting to lowercase")
        text = text.replace("-", " ")
        text = REGEX.sub('', text)
        text = text.lower()
        
        logger.debug("Tokenizing and stemming text")
        text = text.split()
        text = list(map(STEMMER.stem, text))
        
        logger.debug("Calculating word frequencies")
        freq = Counter(text)
        
        logger.debug("Creating vector based on stemmed keywords")
        vector = [freq[category] for category in stemmed_keywords]
        
        logger.info("Normalizing vector")
        normalized_vector = normalize(np.array(vector).reshape((1, -1)), norm="l1", axis=1)
        logger.debug("Normalized vector shape: %s", normalized_vector.shape)
        
        logger.info("Encrypting normalized vector")
        encrypted_vector = client.quantize_encrypt_serialize(normalized_vector)
        logger.info("Encryption complete. Encrypted vector size: %d bytes", len(encrypted_vector))
        
        logging.info("Successfully processed search history")
        logger.info("-" * 30)  
        return encrypted_vector
    except Exception as e:
        logger.error("Error in process_search_history: %s", str(e), exc_info=True)
        raise

def send_search_history_to_server(search_history):
    logger.info("Starting process to send encrypted search history to server")
    try:
        endpoint = f"{SERVER_ADDRESS}/recieve_search_history"
        headers = {'Content-Type': 'application/json'}

        search_history_str = base64.b64encode(search_history).decode('utf-8')
        payload = {"search_history": search_history_str}
        logger.debug(f"Payload size: {len(search_history_str)} bytes")

        logger.info(f"Sending POST request to {endpoint}")
        response = requests.post(endpoint, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info("Received 200 OK response from server")
            raw_bytes = base64.b64decode(response.json()["prediction"])
            categories = response.json()["categories"]
            logger.debug(f"Received {len(categories)} categories from server")

            # Decrypt vector
            logger.info("Starting decryption of received vector")
            try: 
                vector = client.deserialize_decrypt_dequantize(raw_bytes)
                vector = vector[0].tolist()
                logger.debug(f"Decrypted vector length: {len(vector)}")
            except Exception as e:
                logger.error(f"Error during decryption: {str(e)}", exc_info=True)
                raise

            predictions = dict(zip(categories, vector))
            logger.debug("Created predictions dictionary")
            predictions = clean_normalize_predictions(predictions)
            logger.info("Cleaned and normalized predictions")

            # Log predictions
            logger.info("Predictions received and decrypted from server:")
            display_predictions(predictions)

            new_predictions = get_new_prediction(predictions)
            logger.info("Updated predictions:")
            display_predictions(new_predictions)

            return predictions
        else: 
            logger.warning(f"Server returned unexpected status code: {response.status_code}")
            logger.debug(f"Response content: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to server: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error in send_search_history_to_server: {str(e)}", exc_info=True)