import os
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, disconnect
from dotenv import load_dotenv
from actualAI import get_groq_response

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret!')
socketio = SocketIO(app, cors_allowed_origins='*')  # Allow all origins

# Memory storage for each WebSocket connection and request counts
memory_store = {}
request_counts = {}

# Constants
ACCESS_TOKEN = "222001313@ump.ac.za"
MAX_REQUESTS = 3

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['GET'])
def handle_ask():
    token = request.args.get('access_token')
    question = request.args.get('question')

    if token != ACCESS_TOKEN:
        return jsonify({"error": "Invalid access token"}), 403

    if token not in request_counts:
        request_counts[token] = 0

    if request_counts[token] >= MAX_REQUESTS:
        return jsonify({"error": "Request limit exceeded"}), 429

    request_counts[token] += 1

    # Generate the response using the actualAI function
    response = get_groq_response(question, [])

    return jsonify({"response": response})

@socketio.on('connect')
def handle_connect():
    print(f"Connection from: {request.headers.get('Origin')}")
    # Initialize memory for this WebSocket connection
    memory_store[request.sid] = []

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in memory_store:
        del memory_store[request.sid]
    print("Memory for this connection cleared.")

@socketio.on('message')
def handle_message(message):
    print(f"Received message: {message}")
    # Store message in memory for this WebSocket
    memory_store[request.sid].append(message)
    # Use the memory context when getting the response
    response = get_groq_response(message, memory_store[request.sid])
    emit('response', response)

if __name__ == '__main__':
    print("WebSocket server started")
    socketio.run(app, host='0.0.0.0', port=8765)
