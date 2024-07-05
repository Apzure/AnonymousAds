from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=["GET"])
def ping():
    return jsonify({"status": "success"})

@app.route('/public_key', methods=['POST'])
def recieve_key():
    data = request.get_json()
    print(f"Received data: {data}")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(port=5001, debug=True, host='0.0.0.0')
