from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import os
from dotenv import load_dotenv, set_key, find_dotenv
import requests
import traceback

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        dotenv_path = find_dotenv()
        load_dotenv(dotenv_path)

        if request.method == 'POST':
            client_id = request.form.get('client_id')
            client_secret = request.form.get('client_secret')
            
            set_key(dotenv_path, 'REDDIT_CLIENT_ID', client_id)
            set_key(dotenv_path, 'REDDIT_CLIENT_SECRET', client_secret)
            
            load_dotenv(dotenv_path, override=True)
            
            return redirect(url_for('dashboard'))
        
        client_id = os.getenv('REDDIT_CLIENT_ID', '')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
        
        return render_template('dashboard.html', client_id=client_id, client_secret=client_secret)

    @app.route('/call_reddit_export', methods=['GET'])
    def call_reddit_export():
        try:
            # Call the Reddit export API
            response = requests.get('http://localhost:5001/reddit/export', timeout=30)
            
            if response.status_code == 200:
                # If successful, return the file content and headers
                return (response.content, 
                        response.status_code, 
                        {'Content-Type': response.headers['Content-Type'],
                         'Content-Disposition': response.headers['Content-Disposition']})
            else:
                # If there's an error, try to parse JSON response
                try:
                    error_json = response.json()
                    return jsonify(error_json), response.status_code
                except ValueError:
                    # If JSON parsing fails, return the raw text
                    return jsonify({"error": response.text}), response.status_code
        except requests.RequestException as e:
            return jsonify({"error": f"Request failed: {str(e)}"}), 500
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}\n{traceback.format_exc()}"
            print(error_message)  # Log the full error
            return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

    return app