import os
import requests
import json
import logging
import pickle


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
PREDICT_FILENAME = "./tmp/predict.txt"
num_req_made = 0

### Prediction operations ###

def old_pred_exists(curr_pred):
    os.makedirs(os.path.dirname(PREDICT_FILENAME), exist_ok=True)
    return os.path.exists(PREDICT_FILENAME) and os.path.getsize(PREDICT_FILENAME) != 0
        
def read_pred():
    try:
        with open(PREDICT_FILENAME, 'rb') as file:
            if prediction := pickle.load(file):
                return prediction
            else:
                raise ValueError("Prediction file is empty")
    except FileNotFoundError:
        logger.error(f"Prediction file '{PREDICT_FILENAME}' not found")
        raise
    except IOError as e:
        logger.error(f"Error reading Prediction file: {e}")
        raise

def write_prediction(new_prediction):
    try:
        with open(PREDICT_FILENAME, 'wb+') as file:
            pickle.dump(new_prediction, file)
        logger.info(f"Prediction file '{PREDICT_FILENAME}' has been written to.")
    except FileNotFoundError:
        logger.error(f"Prediction file '{PREDICT_FILENAME}' not found")
        raise
    except IOError as e:
        logger.error(f"Error writing Prediction file: {e}")
        raise
    
def get_new_prediction(curr_pred):
    global num_req_made
    
    num_req_made += 1
    if old_pred_exists(curr_pred):
        old_pred = read_pred()
        weight = 1 / (num_req_made + 1)
        for key in old_pred:
            curr_pred[key] += (1 - weight) * old_pred[key] + weight * curr_pred[key]

    curr_pred = clean_normalize_predictions(curr_pred)
    write_prediction(curr_pred)
    return curr_pred

def clean_normalize_predictions(predictions):
    sum_pred = 0
    for category in predictions:
        if predictions[category] <= 0.01:
            predictions[category] = 0
        sum_pred += predictions[category]
    
    for category in predictions:
        predictions[category] /= sum_pred
    return predictions
    
def sort_predictions(predictions):
    return list(sorted(predictions.items(), key=lambda pair: pair[1], reverse=True))
    
def display_predictions(predictions):
    predictions = sort_predictions(predictions)
    logger.info("Predictions recieved:")
    logger.info("-" * 30) 
    for i, (category, probability) in enumerate(predictions, 1):
        category = category.title()
        logger.info(f"{i}. {category:<10} Probability: {probability:.4f}")
    logger.info("-" * 30)  
    logger.info(f"Total predictions: {len(predictions)}")