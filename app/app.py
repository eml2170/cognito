import os
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Configure SocketIO for both development and production
socketio = SocketIO(app, 
                   async_mode='gevent',
                   cors_allowed_origins="*",  # Be more restrictive in production
                   logger=True,
                   engineio_logger=True)

# JSON file path
MESSAGES_FILE = 'messages.json'

# Load existing messages from file at startup
if os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
        try:
            messages = json.load(f)
        except json.JSONDecodeError:
            messages = []
else:
    messages = []  # start empty if file doesn't exist

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """
    When a user connects, send them all previous messages.
    This event fires automatically when a new Socket.IO connection is established.
    """
    # Send the entire message list back only to the newly connected client
    socketio.emit('load_previous_messages', messages, room=request.sid)

@socketio.on('message')
def handle_message(data):
    """
    When a user sends a new message, append it to `messages`,
    save to disk, and broadcast it to everyone.
    `data` is expected to be a dict like: {"username": "Alice", "msg": "Hello world!"}
    """
    # Append the new message to the in-memory list
    messages.append(data)

    # Persist the updated messages list to disk
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    # Broadcast the new message to *all* connected clients
    socketio.emit('message', data)

if __name__ == '__main__':
    socketio.run(app, debug=True)