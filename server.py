import os
import asyncio
import websockets
from dotenv import load_dotenv
from actualAI import get_groq_response

# Load environment variables from .env file
load_dotenv()


def localhost(port): return {f"http://localhost:{port}",f"http://127.0.0.1:{port}" }
# Allowed origins

ALLOWED_ORIGINS = { "https://nextgensell.com" } | localhost(8000)

async def handler(websocket, path):
    origin = websocket.request_headers.get('Origin')
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=1008, reason='Forbidden origin')
        print(f"Connection from forbidden origin: {origin}")
        return
    print(f"Connection from: {origin}")

    try:
        async for message in websocket:
            print(f"Received message: {message}")
            response = get_groq_response(message)
            # response=f"Echo: {message}"
            await websocket.send(response)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

start_server = websockets.serve(handler, "0.0.0.0", 8765)

# Start the server
asyncio.get_event_loop().run_until_complete(start_server)
print("WebSocket server started on ws://0.0.0.0:8765")
asyncio.get_event_loop().run_forever()
