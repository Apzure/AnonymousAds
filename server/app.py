from flask import Flask, request, jsonify, send_from_directory
import requests
import logging
import os
import base64
import pickle
from concrete.ml.deployment import FHEModelServer
from key import write_key, get_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FHE_FILE_PATH_SERVER = "./fhe"



app = Flask(__name__)
server = FHEModelServer(path_dir=FHE_FILE_PATH_SERVER)
try:
    server.load()
except RuntimeError as e:
    logging.error(e)
    raise


@app.route('/recieve_public_key', methods=['POST'])
def recieve_key():
    logging.info("Received a request to /recieve_public_key")
    data = request.data
    try:
        key = pickle.loads(data)
        logging.info("Received key")
        write_key(key)
        return jsonify({"status": "success"}), 200
    except pickle.UnpicklingError as e:
        logging.error("Invalid data received")
        return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/recieve_search_history', methods=['POST'])
def recieve_search_history():
    logging.info("Received a request to /recieve_search_history")
    data = request.json
    try: 
        serialized_evaluation_keys = get_key()
    except Exception as e:
        logging.error(f"Error reading getting keys file: {str(e)}")
        return jsonify({"error": "Internal server error, no key found"}), 500
        
    if data and 'search_history' in data:
        encrypted_input = data['search_history']
        encrypted_input = base64.b64decode(encrypted_input)
        logging.info("Server has received search history")
        
        try: 
            logging.info("Processing encrypted search history...")
            encrypted_result = server.run(encrypted_input, serialized_evaluation_keys)
            encoded_bytes = base64.b64encode(encrypted_result).decode('utf-8')
            
            # Get categories
            CATEGORIES_FILE = "./categories.txt"
            
            try:
                # Check if the file exists
                if not os.path.exists(CATEGORIES_FILE):
                    logging.error(f"Categories file '{CATEGORIES_FILE}' not found")
                    return jsonify({"Error": "Categories file not found on server side"}), 500
                
                with open(CATEGORIES_FILE, 'r') as file:
                    categories = [line.strip() for line in file if line.strip()]
            except Exception as e:
                logging.error(f"Error reading keywords file: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500

            return jsonify({"status": "success", "prediction": encoded_bytes, "categories": categories}), 200
    
        except Exception as e:
            logging.error(f"Error processing encrypted input {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
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
            return jsonify({"Error": "Keywords file not found on server side"}), 500

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
