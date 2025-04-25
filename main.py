from flask import Flask, request, jsonify  
import requests

app = Flask(__name__)

# Original server URL  
ORIGINAL_SERVER_URL = 'http://91.144.20.27:4897/send_captcha'

@app.route('/send_captcha', methods=['POST', 'GET', 'OPTIONS'])
def proxy_request():
    if request.method == 'OPTIONS':
        # Handle CORS preflight request  
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Accept')
        return response

    data = None  
    if request.method == 'POST':
        data = request.get_json()

    # Forward the request to the original server  
    try:
        response = requests.post(ORIGINAL_SERVER_URL, json=data)
        
        # Decode the bytes response if necessary  
        response_data = response.content.decode('utf-8')  # Decode bytes to string  
        json_response = jsonify(eval(response_data))  # Convert string to JSON

        # Log the response for debugging  
        print("Response from original server:", json_response)

        # Set CORS headers on the response  
        json_response.headers.add('Access-Control-Allow-Origin', '*')
        return json_response, response.status_code  
    except requests.exceptions.RequestException as e:
        print("Error occurred while making request to the original server:", e)
        return jsonify({'error': 'Failed to proxy request', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4897)
