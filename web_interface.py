from flask import Flask, request, redirect, session, render_template_string, url_for
import requests
import os
from dotenv import load_dotenv
import logging
import sys
import json
import secrets
import base64
import hashlib

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = os.getenv('CLIENT_ID')
REDIRECT_URI = 'http://localhost:5000/callback'

if not CLIENT_ID:
    logger.error("CLIENT_ID not found in environment variables.")
    logger.error("Please make sure you have set this in your .env file.")
    sys.exit(1)

logger.debug(f"CLIENT_ID: {CLIENT_ID}")

def generate_code_verifier():
    return secrets.token_urlsafe(96)[:128]

def generate_code_challenge(verifier):
    sha256 = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(sha256).decode('utf-8').rstrip('=')

@app.route('/')
def index():
    return render_template_string('''
    <h1>Twitch AI Bot Connector</h1>
    <a href="{{ url_for('login') }}">Connect to Twitch</a>
    ''')

@app.route('/login')
def login():
    code_verifier = generate_code_verifier()
    session['code_verifier'] = code_verifier
    code_challenge = generate_code_challenge(code_verifier)
    
    auth_url = f'https://id.twitch.tv/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=chat:read+chat:edit&code_challenge={code_challenge}&code_challenge_method=S256'
    logger.debug(f"Auth URL: {auth_url}")
    return redirect(auth_url)

@app.route('/callback')
def callback():
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    
    if error:
        logger.error(f"Error in callback: {error} - {error_description}")
        return f"Error: {error} - {error_description}", 400

    code = request.args.get('code')
    if not code:
        logger.error("No code provided in callback")
        return "Error: No code provided", 400

    token_url = 'https://id.twitch.tv/oauth2/token'
    data = {
        'client_id': CLIENT_ID,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code_verifier': session.get('code_verifier')
    }
    logger.debug(f"Token request data: {json.dumps(data, indent=2)}")
    
    try:
        r = requests.post(token_url, data=data)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in token request: {str(e)}")
        logger.error(f"Response content: {r.text}")
        return f"Error: Failed to obtain access token. Details: {str(e)}", 400

    logger.debug(f"Token response status: {r.status_code}")
    logger.debug(f"Token response content: {r.text}")

    response_data = r.json()
    if 'access_token' not in response_data:
        logger.error(f"Access token not found in response: {response_data}")
        return f"Error: Access token not found in response. Response: {response_data}", 400

    session['access_token'] = response_data['access_token']
    return redirect(url_for('channels'))

@app.route('/channels')
def channels():
    if 'access_token' not in session:
        logger.warning("No access token in session, redirecting to login")
        return redirect(url_for('login'))
    
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {session["access_token"]}'
    }
    logger.debug(f"User request headers: {json.dumps(headers, indent=2)}")
    
    try:
        r = requests.get('https://api.twitch.tv/helix/users', headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in user request: {str(e)}")
        logger.error(f"Response content: {r.text}")
        return f"Error: Failed to fetch user data. Details: {str(e)}", 400

    logger.debug(f"User response status: {r.status_code}")
    logger.debug(f"User response content: {r.text}")

    user_data = r.json().get('data', [])
    if not user_data:
        logger.error("No user data found in response")
        return "Error: No user data found in response", 400

    channel_name = user_data[0]['login']
    
    # Here, add the channel to your bot's list of channels
    from channel_manager import add_channel
    add_channel(channel_name)
    
    return render_template_string('''
    <h1>Success!</h1>
    <p>The AI bot has been connected to your channel: {{ channel }}</p>
    ''', channel=channel_name)

if __name__ == '__main__':
    app.run(debug=True)
