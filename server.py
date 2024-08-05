import os
import asyncio
import websockets
import sqlite3
from dotenv import load_dotenv
from actualAI import get_groq_response

# Load environment variables from .env file
load_dotenv()

def localhost(port): return {f"http://localhost:{port}", f"http://127.0.0.1:{port}"}
# Allowed origins
ALLOWED_ORIGINS = {"https://nextgensell.com"} | localhost(5500)

# SQLite3 database file
DB_FILE = 'conversations.db'

# Function to get conversation history from the database
def get_conversation_history(websocket_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT message FROM messages WHERE websocket_id = ? ORDER BY timestamp', (websocket_id,))
    messages = [row[0] for row in c.fetchall()]
    conn.close()
    return messages

# Function to store a message in the database
def store_message(websocket_id, message):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO messages (websocket_id, message) VALUES (?, ?)', (websocket_id, message))
    conn.commit()
    conn.close()

async def handler(websocket, path):
    origin = websocket.request_headers.get('Origin')
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008, reason='Forbidden origin')
        print(f"Connection from forbidden origin: {origin}")
        return
    print(f"Connection from: {origin}")

    # Use a unique identifier for each WebSocket connection
    websocket_id = str(id(websocket))

    try:
        async for message in websocket:
            print(f"Received message: {message}")

            # Store message in the database
            store_message(websocket_id, message)

            # Retrieve the conversation history for this WebSocket
            conversation_history = get_conversation_history(websocket_id)

            # Get response using the conversation history
            response = get_groq_response(message, conversation_history)
            await websocket.send(response)

            # Store the response in the database
            store_message(websocket_id, response)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

    finally:
        # Clean up memory for this WebSocket connection
        print("Memory for this connection cleared.")

start_server = websockets.serve(handler, "0.0.0.0", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started on ws://0.0.0.0:8765")
asyncio.get_event_loop().run_forever()
