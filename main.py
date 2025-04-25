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
    print("Starting Flask server...")
    app.run(host='127.0.0.1', port=4897)

# ---------- Flet UI ----------
server_process = None

def main(page: ft.Page):
    global server_process
    page.title = "Flask Proxy Controller"
    page.scroll = ft.ScrollMode.AUTO
    log_box = ft.TextField(
        multiline=True,
        read_only=True,
        expand=True,
        label="Logs",
        min_lines=15,
        max_lines=30
    )
    start_button = ft.ElevatedButton("تشغيل السيرفر", icon=ft.icons.PLAY_ARROW)
    stop_button = ft.ElevatedButton("إيقاف السيرفر", icon=ft.icons.STOP, disabled=True)

    def start_server(e):
        global server_process
        if server_process is None:
            server_process = Process(target=run_flask)
            server_process.start()
            stop_button.disabled = False
            log_box.value += "Server started on http://localhost:4897\n"
            page.update()

    def stop_server(e):
        global server_process
        if server_process:
            server_process.terminate()
            server_process = None
            stop_button.disabled = True
            log_box.value += "Server stopped.\n"
            page.update()

    start_button.on_click = start_server
    stop_button.on_click = stop_server

    page.add(
        ft.Container(
            content=log_box,
            padding=20,
            expand=True
        ),
        ft.Container(
            content=ft.Row([start_button, stop_button], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.only(top=30, bottom=30)
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
