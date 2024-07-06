from flask import render_template, request, jsonify
from app import app
from .key import send_key_to_server_if_not_sent, send_search_history_to_server
from.process_search_history import init_keywords
import logging

logging.basicConfig(level=logging.INFO)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process_search_history', methods=['POST'])
def process_search_history():
    search_history = request.json.get('searchHistory')
    if not search_history:
        return jsonify({"error": "No search history provided"}), 400
    logging.info("Received search history: %s", search_history)
    
    init_keywords()
    send_key_to_server_if_not_sent()
    
    send_search_history_to_server(search_history)
    return jsonify({"message": "Search history processed successfully"}), 200