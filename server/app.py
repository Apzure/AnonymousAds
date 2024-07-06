from flask import Flask, request, jsonify
import requests
import logging
import os

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/recieve_public_key', methods=['POST'])
def recieve_key():
    logging.info("Received a request to /recieve_public_key")
    data = request.json
    if data and 'key' in data:
        key = data['key']
        logging.info(f"Received key: {key}")
        return jsonify({"status": "success"}), 200
    else:
        logging.error("Invalid data received")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/recieve_search_history', methods=['POST'])
def recieve_search_history():
    logging.info("Received a request to /recieve_search_history")
    data = request.json
    #TODO check if key has been sent? If not return some other http response code to get client to send
    if data and 'search_history' in data:
        history = data['search_history']
        logging.info("Server has received search history: %s", history)
        #TODO Call function to process search history
        return jsonify({"status": "success"}), 200
    else:
        logging.error("Invalid data received")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/get_keywords', methods=['GET'])
def get_keywords():
    logging.info("Received a request to /get_keywords")
    
    KEYWORDS_FILE = "./keywords.txt"
    try:
        # Check if the file exists
        if not os.path.exists(KEYWORDS_FILE):
            logging.error(f"Keywords file '{KEYWORDS_FILE}' not found")
            return jsonify({"error": "Keywords file not found"}), 404

        # Read keywords from the file
        with open(KEYWORDS_FILE, 'r') as file:
            keywords = [line.strip() for line in file if line.strip()]

        logging.info(f"Successfully read {len(keywords)} keywords from the file")
        return jsonify({"keywords": keywords})

    except Exception as e:
        logging.error(f"Error reading keywords file: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    

if __name__ == '__main__':
    app.run(port=5001, debug=True, host='0.0.0.0')
