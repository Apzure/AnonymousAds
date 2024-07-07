from flask import render_template, request, jsonify, send_from_directory
from app import app
from .key import send_key_to_server
from .process_search_history import init_keywords, process_search_history, send_search_history_to_server
import logging
import random
import requests

logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/send_search_history', methods=['POST'])
def send_search_history():
    search_history = request.json.get('searchHistory')
    if not search_history:
        return jsonify({"error": "No search history provided"}), 400
    logging.info("Received search history: %s", search_history)
    
    init_keywords()
    send_key_to_server()
    search_history_vector = process_search_history(search_history) 
    logging.info("Successfully processed search history")
    prediction = send_search_history_to_server(search_history_vector)
    return jsonify(prediction), 200

@app.route('/get_ads', methods = ['POST'])
def send_ads():
    logging.info("-" * 30)
    logging.info("Starting send_ads process")
    
    data = request.json.get('prediction')
    if not data:
        logging.error("No prediction data received in request")
        return jsonify({"error": "No prediction data"}), 400
    
    logging.info(f"Received prediction data with {len(data)} categories")
    
    sorted_ads = sorted(data.items(), key=lambda item: item[1], reverse=True)
    
    # Always select the top two ads
    ads = [ad for ad, _ in sorted_ads[:2]]
    logging.info(f"Top two ads selected: {ads[0]} and {ads[1]}")
    
    good_ads = list(ads)
    logging.info(f"Successfully selected {len(good_ads)} best ad(s)")
    
    # If there are more than two categories, add noisy ads
    remaining_ads = [ad for ad, _ in sorted_ads[2:]]
    for _ in range(2):
        if remaining_ads:
            noisy_ad = random.choice(remaining_ads)
            ads.append(noisy_ad)
            remaining_ads.remove(noisy_ad)
            logging.info(f"Added noisy ad: {noisy_ad}")
    
    logging.info(f"Total ads selected (including noisy): {len(ads)}")
    
    imageURLs = [f"http://server:5001/image/{cat}_1.jpg" for cat in ads]
    for url in imageURLs:
        try:
            response = requests.get(url)
            response.raise_for_status()
            logging.info(f"Successfully retrieved image: {url}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting image {url}: {str(e)}")
    
    goodImageURLs = [f"http://localhost:5001/image/{cat}_1.jpg" for cat in good_ads]
    logging.info(f"Returning {len(goodImageURLs)} good image URLs")
    
    logging.info("Completed send_ads process")
    logging.info("-" * 30)
    return jsonify(goodImageURLs), 200