from flask import render_template, request, jsonify
from app import app


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process_search_history', methods=['POST'])
def process_search_history():
    search_history = request.json.get('searchHistory')
    if not search_history:
        return jsonify({"error": "No search history provided"}), 400

    print("Received search history:", search_history)
    return jsonify({"message": "Search history processed successfully"}), 200