from concrete.ml.sklearn import NeuralNetRegressor
from concrete.ml.deployment import FHEModelDev, FHEModelClient, FHEModelServer
import numpy as np
import torch.nn as nn
from collections import Counter
import re
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
from nltk.stem.porter import PorterStemmer
import os
import requests
import json
import logging 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KEYWORDS_FILENAME = "./tmp/keywords.txt"
STEMMED_KEYWORDS_FILENAME = "./tmp/stemmed_keywords.json"
SERVER_ADDRESS = "http://server:5001/"
REGEX = re.compile('[^a-zA-Z ]')
STEMMER = PorterStemmer()

def init_keywords():
    get_keywords_if_not_got()
    process_keywords()
    
def is_keywords_got():
    return os.path.exists(KEYWORDS_FILENAME)
    
def get_keywords_if_not_got():
    if is_keywords_got():
        logger.info("Keywords have already been got. Skipping.")
        return
    
    endpoint = SERVER_ADDRESS + "/get_keywords"
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            keywords = response.json().get("keywords")
            logger.info("Received keywords from server: %s", keywords)
            
            os.makedirs(os.path.dirname(KEYWORDS_FILENAME), exist_ok=True)
            with open(KEYWORDS_FILENAME, 'w') as file:
                json.dump(keywords, file)
            logger.info(f"Keywords file '{KEYWORDS_FILENAME}' has been created and written to.")
        else:
            logger.warning(f"Server returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to server: {e}")
        
def process_keywords():
    with open(KEYWORDS_FILENAME, 'r') as file:
        keywords = json.load(file)
    stemmed_keywords = list(map(STEMMER.stem, keywords))
    logger.info("stemmed_keywords: %s", stemmed_keywords)
    with open(STEMMED_KEYWORDS_FILENAME, 'w') as file:
        json.dump(stemmed_keywords, file)
    logger.info(f"Stemmed Keywords file '{STEMMED_KEYWORDS_FILENAME}' has been created and written to.")    
    
def process_text(text):   
    with open(STEMMED_KEYWORDS_FILENAME, 'r') as file:
        stemmed_keywords = json.load(file)
         
    text = text.replace("-", " ")
    text = REGEX.sub('', text)
    text = text.lower()
    text = text.split()
    text = list(map(STEMMER.stem, text))
     
    freq = Counter(text)
    vector = [freq[category] for category in stemmed_keywords]
    return vector