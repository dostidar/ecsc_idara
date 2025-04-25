import flet as ft
import subprocess
import threading
import os
from flask import Flask, request, jsonify
import requests
import json
from multiprocessing import Process

# ---------- Flask Server ----------
app = Flask(__name__)
ORIGINAL_SERVER_URL = 'http://91.144.20.27:4897/send_captcha'

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Accept')
    return response

@app.route('/send_captcha', methods=['POST', 'GET', 'OPTIONS'])
def proxy_request():
    if request.method == 'OPTIONS':
        return '', 204
    data = request.get_json() if request.method == 'POST' else None
    try:
        response = requests.post(ORIGINAL_SERVER_URL, json=data)
        response_data = response.content.decode('utf-8')
        json_response = jsonify(json.loads(response_data))
        return json_response, response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to proxy request', 'details': str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=4897)

# ---------- Flet UI ----------
server_process = None

def main(page: ft.Page):
    page.title = "Flask Proxy Controller"
    log_box = ft.TextField(multiline=True, read_only=True, expand=True, label="Logs")
    start_button = ft.ElevatedButton("ØªØ´ØºÙŠÙ„ Ø§Ù„Ø³ÙŠØ±ÙØ±", icon=ft.icons.PLAY_ARROW)
    stop_button = ft.ElevatedButton("Ø¥ÙŠÙ‚Ø§Ù Ø§Ù„Ø³ÙŠØ±ÙØ±", icon=ft.icons.STOP, disabled=True)

    def start_server(e):
        nonlocal server_process
        if server_process is None:
            server_process = Process(target=run_flask)
            server_process.start()
            stop_button.disabled = False
            log_box.value += "Server started on http://localhost:4897\n"
            page.update()

    def stop_server(e):
        nonlocal server_process
        if server_process:
            server_process.terminate()
            server_process = None
            stop_button.disabled = True
            log_box.value += "Server stopped.\n"
            page.update()

    start_button.on_click = start_server
    stop_button.on_click = stop_server

    page.add(ft.Row([start_button, stop_button]), log_box)

if __name__ == "__main__":
    ft.app(target=main)
