from flask import render_template, request, jsonify, send_from_directory
from app import app
from .key import send_key_to_server_if_not_sent
from .process_search_history import init_keywords, process_search_history, send_search_history_to_server
import logging

logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/send_search_history', methods=['POST'])
def send_search_history():
    # return jsonify({"food" : 1, "gaming" : 0.5, "music" : 0.2, "sports" : 0.1, "tv" : 0.25}), 200
    search_history = request.json.get('searchHistory')
    if not search_history:
        return jsonify({"error": "No search history provided"}), 400
    logging.info("Received search history: %s", search_history)
    
    init_keywords()
    send_key_to_server_if_not_sent()
    search_history_vector = process_search_history(search_history) 
    prediction = send_search_history_to_server(search_history_vector)
    logging.info("Successfully predicted")
    return jsonify(prediction), 200

