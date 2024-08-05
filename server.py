import os
import asyncio
import websockets
import sqlite3
from aiohttp import web
from dotenv import load_dotenv
from actualAI import get_groq_response

# Load environment variables from .env file
load_dotenv()

class TokenManager:
    def __init__(self):
        self.valid_tokens = {
            "222001313@ump.ac.za": 3  # Max 3 requests per token
        }

    def validate_and_track_token(self, token):
        if token not in self.valid_tokens:
            return False, "Invalid access token"
        
        if self.valid_tokens[token] <= 0:
            return False, "Token limit exceeded"
        
        self.valid_tokens[token] -= 1
        return True, "Valid token"

class DatabaseManager:
    def __init__(self, db_file='conversations.db'):
        self.db_file = db_file
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                websocket_id TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def get_conversation_history(self, websocket_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('SELECT message FROM messages WHERE websocket_id = ? ORDER BY timestamp', (websocket_id,))
        messages = [row[0] for row in c.fetchall()]
        conn.close()
        return messages

    def store_message(self, websocket_id, message):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('INSERT INTO messages (websocket_id, message) VALUES (?, ?)', (websocket_id, message))
        conn.commit()
        conn.close()

class WebSocketServer:
    def __init__(self, db_manager, token_manager):
        self.db_manager = db_manager
        self.token_manager = token_manager

    async def handler(self, websocket, path):
        origin = websocket.request_headers.get('Origin')
        allowed_origins = {"https://nextgensell.com"} | {f"http://localhost:8000", f"http://127.0.0.1:8000"}
        if origin not in allowed_origins:
            await websocket.close(code=1008, reason='Forbidden origin')
            print(f"Connection from forbidden origin: {origin}")
            return
        print(f"Connection from: {origin}")

        websocket_id = str(id(websocket))

        try:
            async for message in websocket:
                print(f"Received message: {message}")

                # Store message in the database
                self.db_manager.store_message(websocket_id, message)

                # Retrieve the conversation history for this WebSocket
                conversation_history = self.db_manager.get_conversation_history(websocket_id)

                # Get response using the conversation history
                response = get_groq_response(message, conversation_history)
                await websocket.send(response)

                # Store the response in the database
                self.db_manager.store_message(websocket_id, response)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")

        finally:
            print("Memory for this connection cleared.")

class HTTPServer:
    def __init__(self, db_manager, token_manager):
        self.db_manager = db_manager
        self.token_manager = token_manager

    async def http_handler(self, request):
        token = request.query.get('accesstoken')
        question = request.query.get('question')

        if not token or not question:
            return web.Response(text="Missing token or question", status=400)

        valid, message = self.token_manager.validate_and_track_token(token)
        if not valid:
            return web.Response(text=message, status=403)

        # Use the question parameter for the response
        response = get_groq_response(question, [])
        return web.Response(text=response)

async def init_app():
    db_manager = DatabaseManager()
    token_manager = TokenManager()
    http_server = HTTPServer(db_manager, token_manager)
    ws_server = WebSocketServer(db_manager, token_manager)

    app = web.Application()
    app.router.add_get('/', http_server.http_handler)

    # WebSocket server setup
    ws_server_task = websockets.serve(ws_server.handler, "0.0.0.0", 8765)

    return app, ws_server_task

def main():
    app, ws_server_task = asyncio.run(init_app())
    print("WebSocket server started on ws://0.0.0.0:8765")
    print("HTTP server started on http://0.0.0.0:8080")
    web.run_app(app, port=8080)

if __name__ == "__main__":
    main()
