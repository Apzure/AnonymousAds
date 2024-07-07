from flask import render_template, request, jsonify, send_from_directory
from app import app
from .key import send_key_to_server_if_not_sent
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
    send_key_to_server_if_not_sent()
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
        logging.error("No prediction data received")
        return jsonify({"error": "No prediction data"}), 400
    
    sorted_ads = sorted(data.items(), key=lambda item: item[1], reverse=True)
    best_ad, best_prob = sorted_ads[0]
    ads = [best_ad]
    
    # Determine if the second-best ad should be included based on the probability difference
    if len(sorted_ads) > 1 and best_prob - sorted_ads[1][1] < 0.1:  # Threshold for showing the second ad
        ads.append(sorted_ads[1][0])
    
    good_ads = list(ads)
    logging.info("Successfully selected best ads")
    
    remaining_ads = [ad for ad, _ in sorted_ads if ad not in ads]
    if remaining_ads:
        noisy_ad_1 = random.choice(remaining_ads)
        ads.append(noisy_ad_1)
        remaining_ads = [ad for ad in remaining_ads if ad != noisy_ad_1]
    if remaining_ads:
        noisy_ad_2 = random.choice(remaining_ads)
        ads.append(noisy_ad_2)
    
    logging.info("Successfully added noisy ads")
    
    imageURLs = [f"http://server:5001/image/{cat}_1.jpg" for cat in ads]
    for url in imageURLs:
        try:
            requests.get(url)
        except requests.exceptions.RequestException as e:
            logging.error("Error getting image: %s", e)
    
    goodImageURLs = [f"http://localhost:5001/image/{cat}_1.jpg" for cat in good_ads]
    logging.info("Completed send_ads process")
    logging.info("-" * 30)
    return jsonify(goodImageURLs), 200