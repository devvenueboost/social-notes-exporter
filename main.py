from flask import Flask
from src.views import create_app
from src.api_server import app as api_app
import threading

def run_api_server():
    api_app.run(port=5001)  # Run API server on a different port

def create_combined_app():
    app = create_app()
    return app

if __name__ == '__main__':
    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()

    # Run the main Flask app
    combined_app = create_combined_app()
    combined_app.run(debug=True, port=5000)